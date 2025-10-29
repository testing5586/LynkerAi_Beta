#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用 Supabase Python 客户端添加 chart_type 字段
Add chart_type column using Supabase Python client methods
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
    print("🚀 使用 Supabase Python 客户端添加 chart_type 字段")
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
        
        # 检查字段是否已存在
        print("\n🧠 检查 chart_type 字段是否已存在...")
        
        # 尝试查询现有记录
        try:
            existing_records = supabase.table("verified_charts").select("id, chart_id, chart_type").limit(1).execute()
            
            if existing_records.data and len(existing_records.data) > 0:
                record = existing_records.data[0]
                if 'chart_type' in record:
                    print(f"✅ chart_type 字段已存在，默认值: {record.get('chart_type', 'N/A')}")
                else:
                    print("⚠️ chart_type 字段不存在，准备添加...")
                    
                    # 手动插入一条测试记录来触发字段创建
                    test_data = {
                        "user_id": "test_user",
                        "chart_id": "test_chart",
                        "score": 0.0,
                        "confidence": "测试",
                        "matched_keywords": [],
                        "chart_type": "八字"
                    }
                    
                    insert_result = supabase.table("verified_charts").insert(test_data).execute()
                    
                    if insert_result.data:
                        print("✅ 通过插入测试记录成功添加了 chart_type 字段")
                        
                        # 删除测试记录
                        delete_result = supabase.table("verified_charts").delete().eq("user_id", "test_user").execute()
                        
                        if delete_result.data:
                            print("✅ 测试记录已清理")
                        else:
                            print("⚠️ 测试记录清理可能失败")
                    else:
                        print("⚠️ 测试记录插入失败")
                else:
                    print("⚠️ 无法检查现有记录结构")
            else:
                print("⚠️ 无法查询现有记录")
                
        except Exception as e:
            print(f"⚠️ 检查字段时出错: {str(e)}")
        
        # 验证结果
        print("\n🧩 验证字段添加结果...")
        check = supabase.table("verified_charts").select("id, chart_id, chart_type, confidence, created_at").order("created_at", desc=True).limit(5).execute()
        
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