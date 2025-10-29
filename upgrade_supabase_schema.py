#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Supabase 数据库结构升级脚本
Upgrade Supabase Database Schema
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
    print("🚀 Supabase 数据库结构升级工具")
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
        
        # SQL 补丁脚本
        sql_patch = """
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'verified_charts'
        AND column_name = 'chart_type'
    ) THEN
        ALTER TABLE verified_charts ADD COLUMN chart_type TEXT DEFAULT '八字';
        RAISE NOTICE '✅ 已新增字段 chart_type (默认值: 八字)';
    ELSE
        RAISE NOTICE '⚠️ 字段 chart_type 已存在，跳过创建';
    END IF;
END $$;

UPDATE verified_charts
SET chart_type = CASE
    WHEN chart_id ILIKE '%B%' THEN '八字'
    WHEN chart_id ILIKE '%Z%' THEN '紫微'
    ELSE '八字'
END;

ALTER TABLE verified_charts
ALTER COLUMN updated_at SET DEFAULT now();
"""
        
        print("\n🧠 正在执行 Supabase SQL Patch...")
        print("📝 SQL 脚本内容:")
        print(sql_patch)
        
        # 执行 SQL 补丁
        res = supabase.rpc("exec_sql", {"query": sql_patch}).execute() if "exec_sql" in dir(supabase) else None
        
        if res and hasattr(res, 'data'):
            print("✅ SQL 脚本执行完毕")
            if isinstance(res.data, list) and len(res.data) > 0:
                for notice in res.data:
                    if isinstance(notice, dict) and 'message' in notice:
                        print(f"📢 {notice['message']}")
        else:
            print("⚠️ SQL 脚本执行可能失败")
        
        # 验证结果
        print("\n🧩 验证升级结果...")
        check = supabase.table("verified_charts").select("id, user_id, chart_id, chart_type, confidence, created_at").order("created_at", desc=True).limit(5).execute()
        
        if check.data:
            print("✅ 升级成功！最新记录:")
            for r in check.data:
                print(f"  ID={r['id']}, 用户={r['user_id']}, 图表={r['chart_id']}, 类型={r['chart_type']}, 置信度={r.get('confidence')}")
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