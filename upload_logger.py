#!/usr/bin/env python3
"""
Lynker Master Vault 上传日志记录器
自动记录每次文件上传的元数据，打造自学习型知识库
"""

import json
import os
from datetime import datetime
from pathlib import Path

LOG_FILE = "upload_log.json"

def read_file_summary(filepath, max_chars=100):
    """读取文件前N个字符作为摘要"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read(max_chars)
            if len(content) == max_chars:
                content += "..."
            return content.strip()
    except UnicodeDecodeError:
        return "[二进制文件，无法生成摘要]"
    except Exception as e:
        return f"[读取失败: {str(e)}]"

def extract_category_from_result(import_result):
    """从导入结果中提取分类信息"""
    categories = ["project_docs", "api_docs", "dev_brainstorm", "memory"]
    for cat in categories:
        if cat in import_result:
            return cat
    return "unknown"

def log_upload(filename, import_result, uploaded_by="system", filepath=None):
    """
    记录文件上传日志
    
    Args:
        filename: 上传的文件名
        import_result: 导入器返回的结果
        uploaded_by: 上传者标识（默认为 system）
        filepath: 文件路径（用于生成摘要）
    
    Returns:
        dict: 记录的日志条目
    """
    
    # 提取分类信息
    category = extract_category_from_result(import_result)
    
    # 生成文件摘要
    summary = ""
    if filepath and os.path.exists(filepath):
        summary = read_file_summary(filepath)
    
    # 创建日志条目
    log_entry = {
        "filename": filename,
        "category": category,
        "uploaded_by": uploaded_by,
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "import_result": import_result.strip()
    }
    
    # 读取现有日志
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            logs = []
    
    # 添加新条目
    logs.append(log_entry)
    
    # 保存日志
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    
    return log_entry

def get_upload_history(limit=None, category=None):
    """
    获取上传历史记录
    
    Args:
        limit: 限制返回的记录数量
        category: 按分类筛选
    
    Returns:
        list: 日志条目列表
    """
    if not os.path.exists(LOG_FILE):
        return []
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []
    
    # 按分类筛选
    if category:
        logs = [log for log in logs if log.get("category") == category]
    
    # 限制数量（最新的记录）
    if limit:
        logs = logs[-limit:]
    
    return logs

def get_upload_stats():
    """
    获取上传统计信息
    
    Returns:
        dict: 包含各类统计数据
    """
    if not os.path.exists(LOG_FILE):
        return {
            "total_uploads": 0,
            "by_category": {},
            "by_uploader": {},
            "recent_uploads": []
        }
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {
            "total_uploads": 0,
            "by_category": {},
            "by_uploader": {},
            "recent_uploads": []
        }
    
    # 统计分类
    by_category = {}
    by_uploader = {}
    
    for log in logs:
        cat = log.get("category", "unknown")
        uploader = log.get("uploaded_by", "unknown")
        
        by_category[cat] = by_category.get(cat, 0) + 1
        by_uploader[uploader] = by_uploader.get(uploader, 0) + 1
    
    return {
        "total_uploads": len(logs),
        "by_category": by_category,
        "by_uploader": by_uploader,
        "recent_uploads": logs[-5:]  # 最近5条
    }

if __name__ == "__main__":
    # 测试功能
    print("=== Lynker Master Vault 上传日志测试 ===\n")
    
    # 测试记录日志
    test_entry = log_upload(
        filename="测试文档.md",
        import_result="✅ 已导入测试文档.md → project_docs",
        uploaded_by="test_user"
    )
    print(f"✅ 记录成功: {test_entry['filename']}")
    print(f"   分类: {test_entry['category']}")
    print(f"   时间: {test_entry['timestamp']}")
    
    # 测试获取统计
    stats = get_upload_stats()
    print(f"\n📊 上传统计:")
    print(f"   总上传数: {stats['total_uploads']}")
    print(f"   按分类: {stats['by_category']}")
    print(f"   按上传者: {stats['by_uploader']}")
