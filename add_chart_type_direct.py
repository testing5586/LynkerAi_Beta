#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接使用 Supabase Python 客户端添加 chart_type 字段
Add chart_type column using Supabase Python client
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
    print("🚀 直接添加 chart_type 字段工具")
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
        
        # 使用 SQL 直接添加字段
        print("\n🧠 正在添加 chart_type 字段...")
        
        # 添加字段
        sql_add_column = """
        ALTER TABLE verified_charts 
        ADD COLUMN chart_type TEXT DEFAULT '八字';
        """
        
        # 使用 postgrest 的 raw SQL 执行
        response = supabase.table("verified_charts").execute(sql_add_column)
        
        if hasattr(response, 'data') and response.data:
            print("✅ chart_type 字段添加成功")
        else:
            print("⚠️ chart_type 字段可能已存在或添加失败")
        
        # 更新现有记录的 chart_type
        print("\n🧠 正在更新现有记录的 chart_type...")
        
        sql_update = """
        UPDATE verified_charts
        SET chart_type = CASE
            WHEN chart_id ILIKE '%B%' THEN '八字'
            WHEN chart_id ILIKE '%Z%' THEN '紫微'
            ELSE '八字'
        END;
        """
        
        response = supabase.table("verified_charts").execute(sql_update)
        
        if hasattr(response, 'data') and response.data:
            print("✅ 现有记录的 chart_type 更新成功")
        else:
            print("⚠️ 现有记录的 chart_type 更新可能失败")
        
        # 验证结果
        print("\n🧩 验证升级结果...")
        
        check = supabase.table("verified_charts").select("id, chart_id, chart_type, confidence, created_at").order("created_at", desc=True).limit(5).execute()
        
        if check.data:
            print("✅ 升级成功！最新记录:")
            for r in check.data:
                print(f"  ID={r['id']}, 图表={r['chart_id']}, 类型={r['chart_type']}, 置信度={r.get('confidence')}")
        else:
            print("⚠️ 无法验证升级结果")
        
        print("\n" + "=" * 70)
        print("🎉 Supabase 数据库结构升级完成！")
        return True
        
    except Exception as e:
        print(f"❌ 升级失败: {str(e)}")
        return False

if __name__ == "__main__":
    main()