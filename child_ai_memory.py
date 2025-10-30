#!/usr/bin/env python3
"""
==========================================================
子AI记忆仓库模块 - 记录和管理匹配互动记忆
==========================================================
功能：
1. 基于 child_ai_insights 自动生成记忆摘要
2. 追踪用户与匹配对象的互动历史
3. 支持记忆更新（互动次数、最后互动时间）
4. 为前端 React 组件 ChildAIMemoryVault.jsx 提供数据源
"""

# -*- coding: utf-8 -*-
import sys, io
# Only wrap stdout/stderr if not already wrapped
if not hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if not hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
import os
from datetime import datetime
from supabase_init import init_supabase
from google_drive_sync import auto_sync_user_memories


def generate_memory_summary(insight_text, shared_tags):
    """
    从洞察文本和共同标签生成记忆摘要
    
    参数:
        insight_text: 洞察文本（来自 child_ai_insights）
        shared_tags: 共同标签（dict或list）
    
    返回:
        记忆摘要文本
    """
    lines = insight_text.strip().split("\n")
    summary_parts = []
    
    for line in lines:
        if "→" in line:
            core_insight = line.split("→")[-1].strip()
            summary_parts.append(core_insight)
    
    if summary_parts:
        return "，".join(summary_parts)
    else:
        return lines[0].strip() if lines else "暂无摘要"


def extract_tags_from_shared_tags(shared_tags):
    """从 shared_tags 提取标签列表"""
    tags = []
    
    if isinstance(shared_tags, dict):
        for key, value in shared_tags.items():
            if key in ["children", "event_count", "similarity"]:
                continue
            if isinstance(value, str) and value.strip():
                tags.append(value)
    elif isinstance(shared_tags, list):
        tags = [str(tag) for tag in shared_tags if tag]
    
    return tags


def save_or_update_memory(user_id, partner_id, insight_text, shared_tags, similarity, supabase_client=None):
    """保存或更新记忆记录到 Supabase child_ai_memory 表"""
    if supabase_client is None:
        return {"success": False, "error": "Supabase client not provided"}
    
    try:
        summary = generate_memory_summary(insight_text, shared_tags)
        tags = extract_tags_from_shared_tags(shared_tags)
        
        existing = supabase_client.table("child_ai_memory").select("*").eq("user_id", user_id).eq("partner_id", partner_id).execute()
        
        if existing.data and len(existing.data) > 0:
            memory_id = existing.data[0]["id"]
            interaction_count = existing.data[0].get("interaction_count", 0) + 1
            
            result = supabase_client.table("child_ai_memory").update({
                "summary": summary,
                "tags": tags,
                "similarity": similarity,
                "interaction_count": interaction_count,
                "last_interaction": datetime.now().isoformat()
            }).eq("id", memory_id).execute()
            
            print(f"[更新] 已更新记忆：{user_id} ↔ {partner_id} (互动次数：{interaction_count})")
            return {"success": True, "action": "updated", "data": result.data}
        else:
            memory_data = {
                "user_id": user_id,
                "partner_id": partner_id,
                "summary": summary,
                "tags": tags,
                "similarity": similarity,
                "interaction_count": 1,
                "last_interaction": datetime.now().isoformat(),
                "created_at": datetime.now().isoformat()
            }
            
            result = supabase_client.table("child_ai_memory").insert(memory_data).execute()
            
            print(f"[保存] 已保存新记忆：{user_id} ↔ {partner_id}")
            return {"success": True, "action": "created", "data": result.data}
            
    except Exception as e:
        print(f"[错误] 保存记忆失败：{e}")
        return {"success": False, "error": str(e)}


def batch_create_memories_from_insights(user_id, supabase_client=None):
    """从 child_ai_insights 批量创建记忆"""
    if supabase_client is None:
        print("[警告] Supabase client not provided")
        return 0
    
    try:
        insights = supabase_client.table("child_ai_insights").select("*").eq("user_id", user_id).execute()
        
        if not insights.data:
            print(f"[警告] 用户 {user_id} 没有洞察记录")
            return 0
        
        created_count = 0
        updated_count = 0
        
        for insight in insights.data:
            result = save_or_update_memory(
                user_id=insight["user_id"],
                partner_id=insight["partner_id"],
                insight_text=insight["insight_text"],
                shared_tags=insight["shared_tags"],
                similarity=insight["similarity"],
                supabase_client=supabase_client
            )
            
            if result["success"]:
                if result["action"] == "created":
                    created_count += 1
                else:
                    updated_count += 1
        
        print(f"\n[完成] 记忆同步完成：新建 {created_count} 条，更新 {updated_count} 条")
        
        # 自动同步到 Google Drive
        try:
            print("[同步] 正在上传子AI记忆到 Google Drive ...")
            sync_result = auto_sync_user_memories(user_id)
            
            if sync_result.get("success"):
                print("[成功] Google Drive 同步成功！")
            elif sync_result.get("skipped"):
                print(f"[警告] Google Drive 同步跳过：{sync_result.get('error')}")
            else:
                print(f"[警告] Google Drive 同步失败: {sync_result.get('error')}")
        except Exception as e:
            print(f"[警告] Google Drive 同步失败: {e}")
        
        return created_count + updated_count
        
    except Exception as e:
        print(f"[错误] 批量创建记忆失败：{e}")
        return 0


def get_user_memories(user_id, supabase_client=None, limit=10):
    """获取用户的记忆列表（按最后互动时间排序）"""
    if supabase_client is None:
        return []
    
    try:
        result = supabase_client.table("child_ai_memory").select("*").eq("user_id", user_id).order("last_interaction", desc=True).limit(limit).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"[错误] 获取记忆失败：{e}")
        return []


if __name__ == "__main__":
    print("[测试] 测试子AI记忆仓库模块 ...\n")
    
    supabase = init_supabase()
    
    if supabase is None:
        print("[警告] Supabase 未连接，退出测试")
        exit(1)
    
    test_user_id = "u_demo"
    
    print(f"[信息] 正在为用户 {test_user_id} 创建记忆...\n")
    
    count = batch_create_memories_from_insights(test_user_id, supabase)
    
    print(f"\n[信息] 用户 {test_user_id} 的记忆列表：\n")
    memories = get_user_memories(test_user_id, supabase, limit=5)
    
    for i, memory in enumerate(memories, 1):
        print(f"{i}. [关系] {memory['partner_id']}")
        print(f"   [摘要] 摘要：{memory['summary']}")
        print(f"   [标签] 标签：{', '.join(memory['tags']) if memory.get('tags') else '无'}")
        print(f"   [相似度] 相似度：{memory['similarity']}")
        print(f"   [互动] 互动次数：{memory['interaction_count']}")
        print(f"   [时间] 最后互动：{memory['last_interaction']}")
        print()
    
    print(f"[完成] 测试完成！共找到 {len(memories)} 条记忆")

def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        msg = " ".join(str(a) for a in args)
        print(msg.encode('utf-8', 'replace').decode('utf-8'))
