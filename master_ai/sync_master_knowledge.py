#!/usr/bin/env python3
"""
Master AI Knowledge Synchronization Tool
将核心文档同步到 Master AI 的知识库 (Lynker Master Vault)
"""

import os
import sys
import requests
from pathlib import Path

API_BASE = "http://localhost:8008"
DOCS_DIR = Path(__file__).parent.parent / "docs"
VAULT_DIR = Path(__file__).parent.parent / "lynker_master_vault"

KNOWLEDGE_FILES = [
    {
        "path": "docs/lynker_ai_core_index_v2.docx",
        "category": "core_philosophy",
        "description": "灵客AI核心思想索引表"
    },
    {
        "path": "master_ai/README_TMS_v1.md",
        "category": "api_docs",
        "description": "TMS v1.0 系统文档"
    },
    {
        "path": "master_ai/README_PROVIDER_MANAGER.md",
        "category": "api_docs",
        "description": "Multi-Provider 管理器文档"
    },
    {
        "path": "master_ai/QUICK_START.md",
        "category": "project_docs",
        "description": "TMS 快速入门指南"
    },
    {
        "path": "replit.md",
        "category": "project_docs",
        "description": "项目总览与架构文档"
    }
]

def upload_file(file_path: str, category: str, description: str) -> bool:
    """上传单个文件到 Master Vault"""
    full_path = Path(__file__).parent.parent / file_path
    
    if not full_path.exists():
        print(f"⚠️  跳过：{file_path} (文件不存在)")
        return False
    
    try:
        with open(full_path, 'rb') as f:
            files = {'file': (full_path.name, f)}
            data = {'category': category}
            
            response = requests.post(
                f"{API_BASE}/api/master-ai/upload",
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            print(f"✅ 上传成功：{description}")
            return True
        else:
            print(f"❌ 上传失败：{description} ({response.status_code})")
            return False
    
    except Exception as e:
        print(f"❌ 上传异常：{description} - {e}")
        return False

def check_vault_status() -> bool:
    """检查 Master Vault API 是否可用"""
    try:
        response = requests.get(f"{API_BASE}/api/master-ai/context", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_vault_stats():
    """获取 Vault 统计信息"""
    try:
        response = requests.get(f"{API_BASE}/api/master-ai/context", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("total", 0)
        return 0
    except:
        return 0

def main():
    print("=" * 70)
    print("🧠 Master AI Knowledge Synchronization Tool")
    print("=" * 70)
    
    print("\n🔍 检查 Master Vault API 状态...")
    if not check_vault_status():
        print("❌ Master Vault API 未运行")
        print("\n💡 请先启动 Upload API:")
        print("   python master_ai_uploader_api.py")
        sys.exit(1)
    
    print("✅ Master Vault API 正常运行")
    
    before_count = get_vault_stats()
    print(f"\n📊 当前 Vault 文档数量: {before_count}")
    
    print(f"\n📤 开始同步 {len(KNOWLEDGE_FILES)} 个核心文档...")
    print("-" * 70)
    
    success_count = 0
    for item in KNOWLEDGE_FILES:
        if upload_file(item["path"], item["category"], item["description"]):
            success_count += 1
    
    print("-" * 70)
    
    after_count = get_vault_stats()
    print(f"\n📈 同步完成:")
    print(f"   ✅ 成功: {success_count}/{len(KNOWLEDGE_FILES)}")
    print(f"   📚 Vault 文档数量: {before_count} → {after_count}")
    
    if success_count == len(KNOWLEDGE_FILES):
        print("\n🎉 所有核心知识已同步到 Master AI！")
    else:
        print(f"\n⚠️  部分文档同步失败 ({len(KNOWLEDGE_FILES) - success_count} 个)")
    
    print("\n💡 提示:")
    print("   - 访问 http://localhost:8008/chat 测试 Master AI")
    print("   - 访问 http://localhost:8008/master-ai-memory 查看 Memory Dashboard")
    print("=" * 70)

if __name__ == "__main__":
    main()
