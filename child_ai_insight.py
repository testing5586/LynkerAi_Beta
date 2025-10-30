#!/usr/bin/env python3
"""
==========================================================
LynkerAI Child AI Insight Generator - 子AI独立洞察生成器
==========================================================
让每位用户的子AI独立生成匹配共通点报告，节省主AI推理成本。

核心功能：
1. 接收匹配结果（user_id, partner_id, shared_tags, similarity）
2. 使用轻量级规则模板生成Insight报告（无需调用大型模型）
3. 保存到 Supabase 表：child_ai_insights（Supabase不可用时使用本地JSON备份）
4. 主AI仅负责匹配 → 子AI自行分析匹配内容
5. 节省主AI Token：使用规则模板替代大模型，降低运行成本
"""

# -*- coding: utf-8 -*-
import sys, io
# Only wrap stdout/stderr if not already wrapped
if not hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if not hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from datetime import datetime
from typing import List, Optional
import os
import json


# ----------------------------------------------------------
# 子AI表自动建表逻辑
# ----------------------------------------------------------
def init_insight_table(supabase):
    """自动检测并创建子AI洞察表"""
    if supabase is None:
        print("[警告] Supabase 未连接，跳过子AI表检查。")
        return
    
    try:
        # 尝试查询表，检查是否存在
        supabase.table("child_ai_insights").select("id").limit(1).execute()
        print("[成功] Table 'child_ai_insights' already exists.")
    except Exception as e:
        print("[警告] Table 'child_ai_insights' not found, it may need to be created manually.")
        print("[信息] Please create it using the SQL editor in Supabase Dashboard if needed.")
        print("[信息] SQL schema available in: supabase_tables_schema.sql")


# ----------------------------------------------------------
# 核心：子AI Insight 生成器（规则模板）
# ----------------------------------------------------------
def generate_child_insight(
    user_id: str,
    partner_id: str,
    shared_tags,  # 支持 dict 或 list
    similarity: float,
    supabase_client=None
) -> str:
    """
    为匹配双方生成轻量Insight报告（基于规则模板）
    
    参数：
        user_id: 当前用户ID
        partner_id: 匹配对象ID
        shared_tags: 共同特征（dict 或 list）
        similarity: 相似度分数（0-1）
        supabase_client: Supabase客户端（可选）
    
    返回：
        insight_text: 生成的洞察文本
    """
    
    # 1️⃣ 将 shared_tags 转成自然语言描述
    # 支持dict（来自soulmate_matcher）和list格式
    if isinstance(shared_tags, dict):
        # 将字典值转换为字符串列表，过滤掉数字类型的值（如children, event_count）
        tag_values = []
        for k, v in shared_tags.items():
            if k in ["id", "user_id", "created_at", "updated_at"]:
                continue
            if isinstance(v, str) and v:
                tag_values.append(v)
            elif isinstance(v, (int, float)) and k in ["children", "event_count"]:
                # 跳过纯数字字段，不显示在共同特征中
                continue
        tags_text = "、".join(tag_values) if tag_values else "命盘特征相似"
    elif isinstance(shared_tags, list):
        tags_text = "、".join(str(t) for t in shared_tags if t) if shared_tags else "命盘特征相似"
    else:
        tags_text = "命盘特征相似"
    
    # 2️⃣ 定义规则模板（基于相似度分级）
    if similarity >= 0.9:
        relation = "命格高度共振，彼此能深刻理解"
        level_emoji = "[高级]"
    elif similarity >= 0.8:
        relation = "命盘共鸣强烈，适合合作或友谊"
        level_emoji = "[良好]"
    elif similarity >= 0.7:
        relation = "命理特征有一定相似性，适合轻交流"
        level_emoji = "[中等]"
    else:
        relation = "命理有共通点，可能在特定领域产生共鸣"
        level_emoji = "[一般]"
    
    # 3️⃣ 组合 Insight 报告文本
    insight_text = (
        f"{level_emoji} 你与 {partner_id} 的命理相似度为 {similarity:.3f}。\n"
        f"[特征] 共同特征：{tags_text}。\n"
        f"[结论] → {relation}。"
    )
    
    # 4️⃣ 保存到数据库（Supabase优先，失败则保存到本地JSON）
    saved = False
    
    # 尝试保存到Supabase
    if supabase_client:
        try:
            # 将shared_tags转换为JSONB格式（保持原始结构）
            supabase_client.table("child_ai_insights").insert({
                "user_id": user_id,
                "partner_id": partner_id,
                "similarity": similarity,
                "shared_tags": shared_tags if isinstance(shared_tags, dict) else {"tags": shared_tags},
                "insight_text": insight_text,
                "created_at": datetime.now().isoformat()
            }).execute()
           
            print(f"[保存] 子AI Insight 已生成并保存到Supabase：{user_id} ↔ {partner_id} (相似度 {similarity:.3f})")
            saved = True
        except Exception as e:
            print(f"[警告] Supabase保存失败，使用本地备份: {e}")
    
    # 如果Supabase失败，保存到本地JSON文件
    if not saved:
        try:
            os.makedirs("./data", exist_ok=True)
            backup_file = "./data/child_ai_insights_backup.jsonl"
           
            record = {
                "user_id": user_id,
                "partner_id": partner_id,
                "similarity": similarity,
                "shared_tags": shared_tags,
                "insight_text": insight_text,
                "created_at": datetime.now().isoformat()
            }
           
            with open(backup_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
           
            print(f"[保存] 子AI Insight 已生成并保存到本地文件：{user_id} ↔ {partner_id} (相似度 {similarity:.3f})")
            saved = True
        except Exception as e:
            print(f"[警告] 本地文件保存失败: {e}")
    
    if not saved:
        print(f"[信息] 子AI Insight 已生成（未保存）：{user_id} ↔ {partner_id}")
    
    return insight_text


# ----------------------------------------------------------
# 批量生成Insight（用于主AI集成）
# ----------------------------------------------------------
def batch_generate_insights(user_id: str, matches: list, supabase_client=None) -> List[dict]:
    """
    批量为匹配结果生成子AI洞察
    
    参数：
        user_id: 当前用户ID
        matches: 匹配结果列表（来自soulmate_matcher）
        supabase_client: Supabase客户端（可选）
    
    返回：
        insights: 生成的洞察列表
    """
    insights = []
    
    for match in matches:
        partner_id = match.get("matched_user_id") or match.get("match_user_id") or match.get("partner_id")
        similarity = match.get("similarity", 0.0)
        shared_tags = match.get("shared_tags", {})
        
        if not partner_id:
            continue
        
        # 生成单个Insight
        insight_text = generate_child_insight(
            user_id=user_id,
            partner_id=partner_id,
            shared_tags=shared_tags,
            similarity=similarity,
            supabase_client=supabase_client
        )
        
        insights.append({
            "user_id": user_id,
            "partner_id": partner_id,
            "similarity": similarity,
            "shared_tags": shared_tags,
            "insight_text": insight_text
        })
    
    return insights


# ----------------------------------------------------------
# 主入口函数（供外部调用）
# ----------------------------------------------------------
def run_child_ai_insight(user_id: str, matches: list, supabase=None):
    """
    子AI洞察生成器主入口
    
    参数：
        user_id: 当前用户ID
        matches: 匹配结果列表
        supabase: Supabase客户端（可选）
    
    返回：
        insights: 生成的洞察列表
    """
    print("\n[启动] 正在启动子AI Insight生成器 ...")
    
    # 检查并初始化表
    init_insight_table(supabase)
    
    # 批量生成Insight
    insights = batch_generate_insights(user_id, matches, supabase)
    
    print(f"\n[完成] 子AI共生成 {len(insights)} 条洞察报告")
    
    return insights


# ----------------------------------------------------------
# 测试代码（仅开发时使用）
# ----------------------------------------------------------
if __name__ == "__main__":
    from supabase_init import init_supabase
    
    print("[测试] 测试子AI Insight生成器 ...")
    
    # 初始化Supabase
    supabase = init_supabase()
    
    # 测试数据
    test_matches = [
        {
            "match_user_id": "u_test1",
            "similarity": 0.911,
            "shared_tags": ["设计行业", "晚婚", "母缘浅"]
        },
        {
            "match_user_id": "u_test2",
            "similarity": 0.756,
            "shared_tags": ["母缘浅", "无子女"]
        }
    ]
    
    # 运行测试
    insights = run_child_ai_insight("u_demo", test_matches, supabase)
    
    # 输出结果
    print("\n[结果] 生成的Insight:")
    for insight in insights:
        print(f"\n{'-'*60}")
        print(insight["insight_text"])

def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        msg = " ".join(str(a) for a in args)
        print(msg.encode('utf-8', 'replace').decode('utf-8'))
