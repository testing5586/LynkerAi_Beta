#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
添加 chart_type 字段到 verified_charts 表
Add chart_type column to verified_charts table
"""

import os
import sys
from supabase import create_client
from dotenv import load_dotenv

# Set console encoding for Windows
if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def main():
    print("=" * 70)
    print("🚀 添加 chart_type 字段工具")
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
        # 初始化 Supabase 客户端
        supabase = create_client(url, key)
        print(f"✅ 成功连接到 Supabase")
        print(f"📊 URL: {url}")
        
        # 添加 chart_type 字段
        print("\n🧠 正在添加 chart_type 字段...")
        
        # 使用 SQL 添加字段
        sql_add_column = """
        ALTER TABLE verified_charts 
        ADD COLUMN chart_type TEXT DEFAULT '八字';
        """
        
        res = supabase.rpc("exec_sql", {"query": sql_add_column}).execute()
        
        if res and hasattr(res, 'data'):
            print("✅ chart_type 字段添加成功")
        else:
            print("⚠️ chart_type 字段可能已存在或添加失败")
        
        # 验证字段是否添加成功
        print("\n🧩 验证字段添加结果...")
        check = supabase.table("verified_charts").select("id, chart_type").limit(1).execute()
        
        if check.data and len(check.data) > 0:
            record = check.data[0]
            if 'chart_type' in record:
                print(f"✅ 验证成功！chart_type 字段已存在，默认值: {record.get('chart_type', 'N/A')}")
            else:
                print("⚠️ chart_type 字段可能未正确添加")
        else:
            print("⚠️ 无法验证字段添加结果")
        
        print("\n" + "=" * 70)
        print("🎉 chart_type 字段添加完成！")
        return True
        
    except Exception as e:
        print(f"❌ 添加字段失败: {str(e)}")
        return False

if __name__ == "__main__":
    main()