#!/usr/bin/env python3
"""
用户画像聚合器 - 每日定时任务
User Insights Aggregator - Daily Cron Job
"""

import sys
import os
from datetime import datetime, timedelta
from collections import Counter
from typing import Dict, List, Any

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from admin_dashboard.user_events.supabase_client import get_client


def run_daily_aggregation():
    """
    执行每日聚合任务：
    1. 统计近 7 天每个用户的事件
    2. 提取高频关注点（concerns）
    3. 计算情绪倾向
    4. 判断是否达到推送阈值
    5. 更新 user_insights 表
    """
    print("=" * 60)
    print("🔄 开始用户画像聚合任务")
    print("=" * 60)
    
    supabase = get_client()
    if not supabase:
        print("❌ 数据库连接失败")
        return
    
    # 1. 查询近 7 天事件
    seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
    
    try:
        result = supabase.table("user_events")\
            .select("*")\
            .gte("created_at", seven_days_ago)\
            .execute()
        
        if not hasattr(result, 'data'):
            print("⚠️ 查询事件失败")
            return
        
        events = result.data or []  # type: ignore
        print(f"📊 近 7 天事件总数: {len(events)}")
        
        # 2. 按用户分组
        user_events: Dict[int, List[Dict]] = {}
        for event in events:
            user_id = event.get("user_id")
            if user_id:
                if user_id not in user_events:
                    user_events[user_id] = []
                user_events[user_id].append(event)
        
        print(f"👥 活跃用户数: {len(user_events)}")
        
        # 3. 为每个用户生成画像
        updated_count = 0
        
        for user_id, events_list in user_events.items():
            insight = _generate_user_insight(user_id, events_list)
            
            # UPSERT 到 user_insights
            try:
                supabase.table("user_insights").upsert(insight).execute()
                updated_count += 1
                print(f"  ✅ 更新用户 {user_id} 画像: {insight['emotion_tendency']}, 事件数={insight['last_7d_event_count']}, 推送就绪={insight['push_ready']}")
            except Exception as e:
                print(f"  ❌ 更新用户 {user_id} 失败: {e}")
        
        print("\n" + "=" * 60)
        print(f"✅ 聚合任务完成，更新 {updated_count} 个用户画像")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 聚合任务失败: {e}")
        import traceback
        traceback.print_exc()


def _generate_user_insight(user_id: int, events: List[Dict]) -> Dict[str, Any]:
    """为单个用户生成画像"""
    event_count = len(events)
    
    # 提取关注点（宫位、标签）
    concerns = []
    for event in events:
        payload = event.get("event_payload", {})
        
        if isinstance(payload, dict):
            # 提取宫位
            if "palace" in payload:
                concerns.append(payload["palace"])
            
            # 提取标签
            if "tags" in payload and isinstance(payload["tags"], list):
                concerns.extend(payload["tags"])
    
    # 统计高频关注点（Top 3）
    concern_counter = Counter(concerns)
    top_concerns = [item for item, count in concern_counter.most_common(3)]
    
    # 统计情绪倾向
    emotions = [e.get("emotion_label") for e in events if e.get("emotion_label")]
    emotion_counter = Counter(emotions)
    
    if emotion_counter:
        emotion_tendency = emotion_counter.most_common(1)[0][0]
    else:
        emotion_tendency = "neutral"
    
    # 判断推送就绪（7天事件≥5 或 FEELING+anxious≥2）
    anxious_feeling_count = sum(
        1 for e in events 
        if e.get("event_type") == "FEELING" and e.get("emotion_label") == "anxious"
    )
    
    push_ready = (event_count >= 5) or (anxious_feeling_count >= 2)
    
    return {
        "user_id": user_id,
        "top_concerns": top_concerns,
        "emotion_tendency": emotion_tendency,
        "last_7d_event_count": event_count,
        "push_ready": push_ready,
        "updated_at": datetime.now().isoformat()
    }


if __name__ == "__main__":
    run_daily_aggregation()
