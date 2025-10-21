#!/usr/bin/env python3
"""
==========================================================
Lynker Master Vault 知识上下文 API
==========================================================
功能：
1. 提供 Vault 知识摘要的 REST API
2. 支持按类别筛选
3. 可与前端 AI 控制台集成
4. 支持文件上传和自动导入
"""

from flask import Flask, jsonify, request, send_file
from pathlib import Path
from werkzeug.utils import secure_filename
import yaml
import os
import tempfile
import subprocess

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

BASE_DIR = Path("lynker_master_vault")
INDEX_FILE = BASE_DIR / "index.yaml"
UPLOAD_FOLDER = Path(tempfile.gettempdir()) / "vault_uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {'md', 'txt', 'pdf', 'docx', 'doc'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

@app.route("/", methods=["GET"])
def index():
    """返回上传器页面"""
    try:
        return send_file("master_vault_uploader.html")
    except:
        return jsonify({"error": "Uploader page not found"}), 404

@app.route("/api/master-ai/upload", methods=["POST"])
def upload_file():
    """文件上传端点"""
    
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    # 检查文件名
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
    
    # 检查文件类型
    if not allowed_file(file.filename):
        return jsonify({
            "error": f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        }), 400
    
    try:
        # 安全处理文件名
        filename = secure_filename(file.filename or "")
        
        # 保存到临时目录
        temp_path = UPLOAD_FOLDER / filename
        file.save(str(temp_path))
        
        # 调用 master_ai_importer.py 导入文件
        result = subprocess.run(
            ['python', 'master_ai_importer.py', 'import', str(temp_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # 解析输出获取分类
        output = result.stdout
        category = "unknown"
        
        if "→" in output:
            # 提取分类信息
            parts = output.split("→")
            if len(parts) >= 2:
                category = parts[1].split("/")[0].strip()
        
        # 删除临时文件
        if temp_path.exists():
            temp_path.unlink()
        
        return jsonify({
            "success": True,
            "filename": filename,
            "category": category,
            "path": f"lynker_master_vault/{category}/{filename}",
            "message": output.strip()
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Import timeout"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 Lynker Master Vault Context API + 文件上传器")
    print("=" * 60)
    print()
    print("📍 端点:")
    print("   GET  /                           - 上传器页面")
    print("   POST /api/master-ai/upload       - 上传文件")
    print("   GET  /api/master-ai/context      - 获取知识摘要")
    print("   GET  /api/master-ai/categories   - 获取类别统计")
    print("   GET  /api/master-ai/index        - 获取索引")
    print("   GET  /api/master-ai/search?q=... - 搜索文档")
    print("   GET  /api/master-ai/health       - 健康检查")
    print()
    print("🌐 访问上传器:")
    print("   http://localhost:8080/")
    print()
    print("🚀 启动中...")
    print("=" * 60)
    
    app.run(host="0.0.0.0", port=8080, debug=True)
