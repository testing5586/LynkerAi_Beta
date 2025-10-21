#!/usr/bin/env python3
"""
==========================================================
Lynker Master Vault 文档导入器
==========================================================
功能：
1. 自动识别文档类别（项目文档、开发思路、API文档）
2. 导入文档到对应分类目录
3. 维护全局索引（YAML格式）
"""

import os
import json
import shutil
from pathlib import Path
import yaml

BASE_DIR = Path("lynker_master_vault")
INDEX_FILE = BASE_DIR / "index.yaml"

def ensure_dirs():
    """确保所有目录存在"""
    (BASE_DIR / "project_docs").mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "dev_brainstorm").mkdir(exist_ok=True)
    (BASE_DIR / "api_docs").mkdir(exist_ok=True)
    (BASE_DIR / "memory").mkdir(exist_ok=True)

def categorize_doc(filename):
    """自动识别文档类别"""
    lower = filename.lower()
    
    # UI/设计相关
    if any(x in lower for x in ["ui", "design", "dashboard", "client", "frontend"]):
        return "project_docs"
    
    # API/后端相关
    if any(x in lower for x in ["api", "auth", "supabase", "drive", "oauth", "backend", "flask"]):
        return "api_docs"
    
    # AI/命理/玄学相关
    if any(x in lower for x in ["ai", "guru", "iron", "命理", "同命", "玄学", "太玄", "铁板", "八字", "紫微"]):
        return "dev_brainstorm"
    
    # 默认归类为项目文档
    return "project_docs"

def import_doc(filepath):
    """导入文档到 Vault"""
    ensure_dirs()
    
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在：{filepath}")
        return False
    
    # 识别类别
    category = categorize_doc(filepath)
    
    # 复制文件
    target = BASE_DIR / category / os.path.basename(filepath)
    shutil.copy(filepath, target)
    
    # 更新索引
    update_index(os.path.basename(filepath), category, filepath)
    
    print(f"✅ 已导入 {filepath} → {category}/{os.path.basename(filepath)}")
    return True

def update_index(filename, category, original_path=""):
    """更新全局索引"""
    if INDEX_FILE.exists():
        try:
            index = yaml.safe_load(INDEX_FILE.read_text()) or {}
        except:
            index = {}
    else:
        index = {}
    
    # 初始化类别
    if category not in index:
        index[category] = []
    
    # 添加文件信息
    file_info = {
        "filename": filename,
        "imported_at": str(Path(original_path).stat().st_mtime) if original_path and os.path.exists(original_path) else ""
    }
    
    # 检查是否已存在
    existing = [f for f in index[category] if isinstance(f, dict) and f.get("filename") == filename]
    if not existing:
        index[category].append(file_info)
    
    # 保存索引
    INDEX_FILE.write_text(yaml.safe_dump(index, allow_unicode=True, sort_keys=False))
    print(f"📚 索引已更新 → {INDEX_FILE}")

def list_vault():
    """列出 Vault 中的所有文档"""
    if not INDEX_FILE.exists():
        print("📦 Vault 为空")
        return
    
    index = yaml.safe_load(INDEX_FILE.read_text()) or {}
    
    print("=" * 60)
    print("📚 Lynker Master Vault 文档列表")
    print("=" * 60)
    
    for category, files in index.items():
        print(f"\n📁 {category}")
        print("-" * 60)
        for f in files:
            if isinstance(f, dict):
                print(f"   - {f.get('filename', 'Unknown')}")
            else:
                print(f"   - {f}")
    
    print("=" * 60)

def search_vault(keyword):
    """在 Vault 中搜索文档"""
    results = []
    
    for category in ["project_docs", "dev_brainstorm", "api_docs"]:
        path = BASE_DIR / category
        if not path.exists():
            continue
        
        for file in path.glob("*"):
            if file.is_file():
                # 检查文件名
                if keyword.lower() in file.name.lower():
                    results.append((category, file.name))
                    continue
                
                # 检查文件内容
                try:
                    content = file.read_text(errors='ignore')
                    if keyword.lower() in content.lower():
                        results.append((category, file.name))
                except:
                    pass
    
    if results:
        print(f"🔍 搜索结果 (关键词: {keyword})")
        print("=" * 60)
        for category, filename in results:
            print(f"   {category}/{filename}")
        print("=" * 60)
    else:
        print(f"❌ 未找到包含 '{keyword}' 的文档")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("=" * 60)
        print("📥 Lynker Master Vault 文档导入器")
        print("=" * 60)
        print()
        print("用法：")
        print("  导入文档：python master_ai_importer.py import <文件路径>")
        print("  列出文档：python master_ai_importer.py list")
        print("  搜索文档：python master_ai_importer.py search <关键词>")
        print()
        print("示例：")
        print("  python master_ai_importer.py import OAUTH_CALLBACK_GUIDE.md")
        print("  python master_ai_importer.py list")
        print("  python master_ai_importer.py search oauth")
        print("=" * 60)
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command == "import" and len(sys.argv) >= 3:
        import_doc(sys.argv[2])
    elif command == "list":
        list_vault()
    elif command == "search" and len(sys.argv) >= 3:
        search_vault(sys.argv[2])
    else:
        print("❌ 未知命令，使用 'python master_ai_importer.py' 查看帮助")
