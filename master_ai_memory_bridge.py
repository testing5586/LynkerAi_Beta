#!/usr/bin/env python3
"""
Master AI Memory Bridge - 上传日志到子AI记忆系统的桥接模块
自动将文件上传记录同步到 child_ai_memory 表，实现知识库的"自学习记忆"
"""

import json
import os
from datetime import datetime
from supabase_init import get_supabase

LOG_FILE = "upload_log.json"
LOCAL_BACKUP = "child_ai_memory_backup.json"

def bridge_new_uploads_to_memory(limit=3):
    """
    将最新上传的文件同步到子AI记忆系统
    
    Args:
        limit: 同步最近N条记录（默认3条）
    
    Returns:
        dict: 同步结果统计
    """
    
    # 获取 Supabase 客户端
    supabase = get_supabase()
    if not supabase:
        print("⚠️ Supabase 未配置，跳过记忆同步")
        return {"success": False, "error": "Supabase not configured"}
    
    # 检查日志文件
    if not os.path.exists(LOG_FILE):
        print("⚠️ 没有找到 upload_log.json")
        return {"success": False, "error": "Log file not found"}
    
    # 读取上传日志
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"⚠️ 读取日志失败: {e}")
        return {"success": False, "error": str(e)}
    
    if not logs:
        print("⚠️ 没有可同步的日志记录")
        return {"success": False, "error": "No logs to sync"}
    
    # 只同步最近N条记录
    new_entries = logs[-limit:] if len(logs) > limit else logs
    
    synced_count = 0
    failed_count = 0
    memories = []
    
    for entry in new_entries:
        filename = entry.get("filename", "unknown")
        summary = entry.get("summary", "")
        category = entry.get("category", "uncategorized")
        uploaded_by = entry.get("uploaded_by", "unknown")
        timestamp = entry.get("timestamp", datetime.now().isoformat())
        
        # 构建记忆记录
        memory = {
            "user_id": uploaded_by,
            "partner_id": f"doc_{filename}",  # 以文件名作记忆对象标识
            "summary": summary[:500] if summary else f"文档: {filename}",  # 限制摘要长度
            "tags": [category, "document", "vault"],
            "similarity": 0.95,  # 文档上传默认高相似度
            "interaction_count": 1,
            "last_interaction": timestamp,
            "created_at": timestamp,
            "updated_at": timestamp
        }
        
        try:
            # 插入到 Supabase
            result = supabase.table("child_ai_memory").insert(memory).execute()
            print(f"💾 已同步至子AI记忆: {filename}")
            synced_count += 1
            memories.append(memory)
            
        except Exception as e:
            print(f"⚠️ 同步失败 {filename}: {e}")
            failed_count += 1
    
    # 保存本地备份
    try:
        backup_data = {
            "last_sync": datetime.now().isoformat(),
            "total_synced": synced_count,
            "memories": memories
        }
        
        # 读取现有备份
        existing_backup = []
        if os.path.exists(LOCAL_BACKUP):
            try:
                with open(LOCAL_BACKUP, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    existing_backup = existing_data.get("memories", [])
            except:
                pass
        
        # 合并并保存
        all_memories = existing_backup + memories
        backup_data["memories"] = all_memories[-100:]  # 只保留最近100条
        
        with open(LOCAL_BACKUP, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"⚠️ 本地备份失败: {e}")
    
    # 返回统计结果
    result = {
        "success": True,
        "synced": synced_count,
        "failed": failed_count,
        "total": len(new_entries)
    }
    
    print(f"✅ 共同步 {synced_count} 条新记忆（失败 {failed_count} 条）")
    return result

def get_memory_stats():
    """获取记忆统计信息"""
    supabase = get_supabase()
    if not supabase:
        return {"error": "Supabase not configured"}
    
    try:
        # 查询记忆总数
        result = supabase.table("child_ai_memory").select("*", count="exact").execute()
        total = result.count if hasattr(result, 'count') else len(result.data)
        
        # 按用户分组统计
        by_user = {}
        for memory in result.data:
            user = memory.get("user_id", "unknown")
            by_user[user] = by_user.get(user, 0) + 1
        
        return {
            "total_memories": total,
            "by_user": by_user,
            "recent": result.data[:5] if result.data else []
        }
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 Master AI Memory Bridge")
    print("=" * 60)
    
    # 执行同步
    result = bridge_new_uploads_to_memory()
    
    print("\n📊 统计信息:")
    stats = get_memory_stats()
    if "error" not in stats:
        print(f"   总记忆数: {stats.get('total_memories', 0)}")
        print(f"   按用户: {stats.get('by_user', {})}")
    else:
        print(f"   ⚠️ {stats['error']}")
