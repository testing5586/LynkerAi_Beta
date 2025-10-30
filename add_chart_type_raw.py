#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用原始 SQL 端点添加 chart_type 字段
Add chart_type column using raw SQL endpoint
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Set console encoding for Windows
if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def main():
    print("=" * 70)
    print("🚀 使用原始 SQL 端点添加 chart_type 字段")
    print("=" * 70)
    
    # Load environment variables
    load_dotenv(dotenv_path='../../.env')
    load_dotenv(dotenv_path='.env')
    load_dotenv()
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ 未找到 Supabase 环境变量")
        print("请检查 .env 文件中的 SUPABASE_URL 和 SUPABASE_KEY")
        return False
    
    try:
        # 使用原始 SQL 端点
        rest_url = f"{url}/rest/v1/"
        headers = {
            "apikey": key,
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        # 添加字段的 SQL
        sql_add_column = """
        ALTER TABLE verified_charts 
        ADD COLUMN chart_type TEXT DEFAULT '八字';
        """
        
        # 更新字段的 SQL
        sql_update = """
        UPDATE verified_charts
        SET chart_type = CASE
            WHEN chart_id ILIKE '%B%' THEN '八字'
            WHEN chart_id ILIKE '%Z%' THEN '紫微'
            ELSE '八字'
        END;
        """
        
        print("\n🧠 正在执行 SQL 添加字段...")
        response = requests.post(
            f"{rest_url}rpc/rpc",
            headers=headers,
            json={
                "schema": "public",
                "procedure": "exec_sql",
                "args": {
                    "query": sql_add_column
                }
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'data' in result and result['data']:
                for item in result['data']:
                    if isinstance(item, dict) and 'message' in item:
                        print(f"📢 {item['message']}")
            print("✅ chart_type 字段添加成功")
        else:
            print(f"⚠️ 添加字段响应: {response.status_code}")
        
        print("\n🧠 正在执行 SQL 更新字段...")
        response = requests.post(
            f"{rest_url}rpc/rpc",
            headers=headers,
            json={
                "schema": "public",
                "procedure": "exec_sql",
                "args": {
                    "query": sql_update
                }
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'data' in result and result['data']:
                for item in result['data']:
                    if isinstance(item, dict) and 'message' in item:
                        print(f"📢 {item['message']}")
            print("✅ chart_type 字段更新成功")
        else:
            print(f"⚠️ 更新字段响应: {response.status_code}")
        
        # 验证结果
        print("\n🧩 验证升级结果...")
        response = requests.post(
            f"{rest_url}rpc/rpc",
            headers=headers,
            json={
                "schema": "public",
                "procedure": "exec_sql",
                "args": {
                    "query": "SELECT id, chart_id, chart_type, confidence, created_at FROM verified_charts ORDER BY created_at DESC LIMIT 5"
                }
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'data' in result and result['data']:
                print("✅ 升级成功！最新记录:")
                for r in result['data']:
                    print(f"  ID={r['id']}, 图表={r['chart_id']}, 类型={r['chart_type']}, 置信度={r.get('confidence')}")
            else:
                print("⚠️ 无法验证升级结果")
        else:
            print(f"⚠️ 验证响应: {response.status_code}")
        
        print("\n" + "=" * 70)
        print("🎉 Supabase 数据库结构升级完成！")
        return True
        
    except Exception as e:
        print(f"❌ 升级失败: {str(e)}")
        return False

if __name__ == "__main__":
    main()