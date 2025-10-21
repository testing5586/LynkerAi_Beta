#!/usr/bin/env python3
"""
==========================================================
Lynker Master Vault 知识上下文 API
==========================================================
功能：
1. 提供 Vault 知识摘要的 REST API
2. 支持按类别筛选
3. 可与前端 AI 控制台集成
"""

from flask import Flask, jsonify, request
from pathlib import Path
import yaml

app = Flask(__name__)

BASE_DIR = Path("lynker_master_vault")
INDEX_FILE = BASE_DIR / "index.yaml"

@app.route("/api/master-ai/context", methods=["GET"])
def get_master_context():
    """返回 Lynker Vault 知识摘要"""
    
    category_filter = request.args.get("category")
    max_length = int(request.args.get("max_length", 500))
    
    summaries = []
    
    categories = ["project_docs", "dev_brainstorm", "api_docs"]
    if category_filter:
        categories = [category_filter]
    
    for category in categories:
        path = BASE_DIR / category
        if not path.exists():
            continue
        
        for file in path.glob("*"):
            if file.is_file():
                try:
                    text = file.read_text(errors='ignore')
                    snippet = text[:max_length]
                    
                    summaries.append({
                        "file": file.name,
                        "category": category,
                        "snippet": snippet,
                        "size": len(text),
                        "path": f"lynker_master_vault/{category}/{file.name}"
                    })
                except Exception as e:
                    print(f"⚠️ 读取文件失败：{file.name} - {e}")
    
    return jsonify({
        "total": len(summaries),
        "summaries": summaries
    })

@app.route("/api/master-ai/categories", methods=["GET"])
def get_categories():
    """返回所有类别及文件数"""
    
    categories = {}
    
    for category in ["project_docs", "dev_brainstorm", "api_docs", "memory"]:
        path = BASE_DIR / category
        if path.exists():
            file_count = len(list(path.glob("*")))
            categories[category] = file_count
    
    return jsonify(categories)

@app.route("/api/master-ai/index", methods=["GET"])
def get_index():
    """返回 Vault 索引"""
    
    if not INDEX_FILE.exists():
        return jsonify({"error": "Index not found"}), 404
    
    try:
        index = yaml.safe_load(INDEX_FILE.read_text()) or {}
        return jsonify(index)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/master-ai/search", methods=["GET"])
def search_vault():
    """搜索 Vault 中的文档"""
    
    keyword = request.args.get("q", "").lower()
    if not keyword:
        return jsonify({"error": "Missing query parameter 'q'"}), 400
    
    results = []
    
    for category in ["project_docs", "dev_brainstorm", "api_docs"]:
        path = BASE_DIR / category
        if not path.exists():
            continue
        
        for file in path.glob("*"):
            if file.is_file():
                # 检查文件名
                if keyword in file.name.lower():
                    results.append({
                        "file": file.name,
                        "category": category,
                        "match_type": "filename"
                    })
                    continue
                
                # 检查文件内容
                try:
                    content = file.read_text(errors='ignore')
                    if keyword in content.lower():
                        # 提取关键词上下文
                        idx = content.lower().find(keyword)
                        start = max(0, idx - 100)
                        end = min(len(content), idx + 100)
                        context = content[start:end]
                        
                        results.append({
                            "file": file.name,
                            "category": category,
                            "match_type": "content",
                            "context": context
                        })
                except:
                    pass
    
    return jsonify({
        "query": keyword,
        "total": len(results),
        "results": results
    })

@app.route("/api/master-ai/health", methods=["GET"])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "vault_path": str(BASE_DIR),
        "index_exists": INDEX_FILE.exists()
    })

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 Lynker Master Vault Context API")
    print("=" * 60)
    print()
    print("📍 端点:")
    print("   GET /api/master-ai/context       - 获取知识摘要")
    print("   GET /api/master-ai/categories    - 获取类别统计")
    print("   GET /api/master-ai/index         - 获取索引")
    print("   GET /api/master-ai/search?q=...  - 搜索文档")
    print("   GET /api/master-ai/health        - 健康检查")
    print()
    print("🚀 启动中...")
    print("=" * 60)
    
    app.run(host="0.0.0.0", port=8080, debug=True)
