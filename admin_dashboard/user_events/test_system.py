#!/usr/bin/env python3
"""
用户事件追踪系统完整测试
Full System Test for User Events Tracking
"""

import sys
import os
import time
import requests
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

BASE_URL = "http://127.0.0.1:5000"

def test_track_event(event_data):
    """测试事件追踪 API"""
    url = f"{BASE_URL}/api/events/track"
    response = requests.post(url, json=event_data, timeout=10)
    return response.json()

def test_get_insights(user_id):
    """测试用户画像查询 API"""
    url = f"{BASE_URL}/api/insights/{user_id}"
    response = requests.get(url, timeout=10)
    return response.json()

def test_get_overview():
    """测试事件概览 API"""
    url = f"{BASE_URL}/api/events/stats/overview"
    response = requests.get(url, timeout=10)
    return response.json()

def main():
    print("=" * 60)
    print("🧪 用户事件追踪系统完整测试")
    print("=" * 60)
    
    # 1. 发送测试事件
    print("\n1️⃣ 发送测试事件...")
    
    test_events = [
        {
            "user_id": 3,
            "event_type": "VIEW_PALACE",
            "event_payload": {"palace": "夫妻宫"}
        },
        {
            "user_id": 3,
            "event_type": "QUESTION",
            "event_payload": {"text": "我对婚姻很担心，总是反复焦虑"}
        },
        {
            "user_id": 3,
            "event_type": "FEELING",
            "event_payload": {"text": "今天心情很开心，感觉运势很好"}
        },
        {
            "user_id": 4,
            "event_type": "MARK_RESONANCE",
            "event_payload": {"target": "文章123", "tags": ["廉贞", "破军"]}
        }
    ]
    
    for i, event in enumerate(test_events, 1):
        try:
            result = test_track_event(event)
            emotion = result.get("emotion")
            if emotion:
                print(f"  ✅ 事件 {i}: {event['event_type']} → 情绪={emotion['label']} ({emotion['score']:.2f})")
            else:
                print(f"  ✅ 事件 {i}: {event['event_type']} → 无情绪分析")
        except Exception as e:
            print(f"  ❌ 事件 {i} 失败: {e}")
        
        time.sleep(0.5)
    
    # 2. 查询事件概览
    print("\n2️⃣ 查询事件概览...")
    try:
        overview = test_get_overview()
        print(f"  ✅ 7天事件数: {overview.get('total_events_7d', 0)}")
        print(f"  ✅ 总事件数: {overview.get('total_events_all', 0)}")
        
        emotions = overview.get('emotion_distribution', {})
        if emotions:
            print(f"  ✅ 情绪分布: {emotions}")
    except Exception as e:
        print(f"  ❌ 查询概览失败: {e}")
    
    # 3. 执行聚合
    print("\n3️⃣ 执行用户画像聚合...")
    try:
        from admin_dashboard.user_events.aggregator import run_daily_aggregation
        run_daily_aggregation()
        print("  ✅ 聚合任务完成")
    except Exception as e:
        print(f"  ❌ 聚合失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. 查询用户画像
    print("\n4️⃣ 查询用户画像...")
    for user_id in [3, 4]:
        try:
            insight = test_get_insights(user_id)
            print(f"\n  用户 {user_id} 画像:")
            print(f"    情绪倾向: {insight.get('emotion_tendency')}")
            print(f"    7天事件数: {insight.get('last_7d_event_count')}")
            print(f"    关注点: {insight.get('top_concerns', [])}")
            print(f"    推送就绪: {insight.get('push_ready')}")
        except Exception as e:
            print(f"  ❌ 查询用户 {user_id} 失败: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
    print("\n💡 提示：访问 http://localhost:5000/dashboard 查看可视化面板")

if __name__ == "__main__":
    main()
