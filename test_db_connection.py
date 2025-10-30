#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 Supabase 数据库连接
Test Supabase Database Connection
"""

import os
import sys
import json
from dotenv import load_dotenv
from supabase import create_client

# Set console encoding for Windows
if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

def test_db_connection():
    """测试数据库连接并显示数据"""
    print("=" * 60)
    print("🔍 测试 Supabase 数据库连接")
    print("=" * 60)
    
    # 初始化客户端
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ 未找到 Supabase 环境变量")
        print("请检查 .env 文件中的 SUPABASE_URL 和 SUPABASE_KEY")
        return False
    
    try:
        client = create_client(url, key)
        print(f"✅ 成功连接到 Supabase")
        print(f"📊 URL: {url}")
        
        # 测试读取 verified_charts 表
        print("\n📋 测试读取 verified_charts 表...")
        res = client.table("verified_charts").select("*").limit(3).execute()
        
        if res.data:
            print(f"✅ 找到 {len(res.data)} 条记录")
            for i, record in enumerate(res.data, 1):
                print(f"  {i}. ID: {record.get('id', 'N/A')}")
                print(f"     用户: {record.get('user_id', 'N/A')}")
                print(f"     图表: {record.get('chart_id', 'N/A')}")
                print(f"     得分: {record.get('score', 'N/A')}")
                print(f"     置信度: {record.get('confidence', 'N/A')}")
                print(f"     验证时间: {record.get('verified_at', 'N/A')}")
                print()
        else:
            print("⚠️ verified_charts 表为空")
        
        # 测试读取其他表
        tables_to_check = ["user_events", "user_insights", "life_event_weights", "soulmate_matches"]
        
        for table in tables_to_check:
            print(f"\n📋 测试读取 {table} 表...")
            try:
                res = client.table(table).select("*").limit(1).execute()
                if res.data:
                    print(f"✅ {table} 表存在，有数据")
                else:
                    print(f"⚠️ {table} 表存在但为空")
            except Exception as e:
                print(f"❌ 无法读取 {table} 表: {str(e)[:50]}...")
        
        print("\n" + "=" * 60)
        print("🎉 数据库连接测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")
        return False

if __name__ == "__main__":
    test_db_connection()