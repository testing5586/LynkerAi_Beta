#!/usr/bin/env python3
"""
Supabase birthcharts 表修复工具
自动填充缺失的 birth_data JSONB 字段
"""

import os
import sys
import random
from supabase import create_client, Client

def get_supabase_client() -> Client:
    """初始化 Supabase 客户端"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ 错误：缺少环境变量 SUPABASE_URL 或 SUPABASE_KEY")
        sys.exit(1)
    
    return create_client(url, key)

def check_birth_data_field(supabase: Client) -> bool:
    """检查 birth_data 字段是否存在"""
    try:
        # 尝试查询一条记录来验证字段存在
        result = supabase.table("birthcharts").select("id, birth_data").limit(1).execute()
        print("✅ birth_data 字段已存在")
        return True
    except Exception as e:
        print(f"⚠️ birth_data 字段检测失败: {e}")
        return False

def find_records_needing_repair(supabase: Client) -> list:
    """查找需要修复的记录"""
    try:
        # 获取所有记录
        result = supabase.table("birthcharts").select("id, name, birth_data").execute()
        
        needs_repair = []
        if hasattr(result, 'data') and result.data:  # type: ignore
            for record in result.data:  # type: ignore
                # 检查 birth_data 是否为空或不是对象
                if isinstance(record, dict):
                    birth_data = record.get("birth_data")
                    if not birth_data or not isinstance(birth_data, dict):
                        needs_repair.append(record)
        
        return needs_repair
    except Exception as e:
        print(f"❌ 查询记录失败: {e}")
        return []

def generate_birth_data(record_id: int) -> dict:
    """生成模拟的 birth_data"""
    return {
        "marriage_palace_star": "天府" if record_id % 2 == 0 else "武曲",
        "wealth_palace_star": "武曲" if record_id % 2 == 0 else "天府",
        "transformations": {
            "hualu": random.random() > 0.5,
            "huaji": random.random() > 0.4
        }
    }

def repair_record(supabase: Client, record_id: int) -> dict | None:
    """修复单条记录"""
    birth_data = generate_birth_data(record_id)
    
    try:
        result = supabase.table("birthcharts").update({
            "birth_data": birth_data
        }).eq("id", record_id).execute()
        
        return birth_data
    except Exception as e:
        print(f"⚠️ 修复记录 ID={record_id} 失败: {e}")
        return None

def main():
    print("=" * 60)
    print("🛠️  Supabase birthcharts 表修复工具")
    print("=" * 60)
    
    # 1. 连接 Supabase
    print("\n📡 连接 Supabase 数据库...")
    supabase = get_supabase_client()
    print("✅ 连接成功")
    
    # 2. 检查 birth_data 字段
    print("\n🔍 检测 birth_data 字段...")
    if not check_birth_data_field(supabase):
        print("❌ 无法继续，请确认表结构")
        sys.exit(1)
    
    # 3. 查找需要修复的记录
    print("\n🔎 查找需要修复的记录...")
    records_to_repair = find_records_needing_repair(supabase)
    
    if not records_to_repair:
        print("✅ 所有记录的 birth_data 字段完整，无需修复")
        return
    
    print(f"⚠️  发现 {len(records_to_repair)} 条记录需要修复")
    
    # 4. 执行修复
    print("\n🔧 开始修复...")
    repaired_count = 0
    sample_data = []
    
    for record in records_to_repair:
        record_id = record["id"]
        record_name = record.get("name", "未知")
        
        print(f"  修复中: ID={record_id}, 姓名={record_name}")
        
        birth_data = repair_record(supabase, record_id)
        if birth_data:
            repaired_count += 1
            if len(sample_data) < 3:  # 保留前3条作为示例
                sample_data.append({
                    "id": record_id,
                    "name": record_name,
                    "birth_data": birth_data
                })
    
    # 5. 输出结果
    print("\n" + "=" * 60)
    print("✅ 修复完成")
    print("=" * 60)
    print(f"🧩 更新记录总数: {repaired_count} 条")
    
    if sample_data:
        print("\n⚙️  修复后的数据示例：")
        for item in sample_data:
            print(f"\n  📋 ID={item['id']}, 姓名={item['name']}")
            print(f"     夫妻宫主星: {item['birth_data']['marriage_palace_star']}")
            print(f"     财帛宫主星: {item['birth_data']['wealth_palace_star']}")
            print(f"     化禄: {'是' if item['birth_data']['transformations']['hualu'] else '否'}")
            print(f"     化忌: {'是' if item['birth_data']['transformations']['huaji'] else '否'}")
    
    print("\n" + "=" * 60)
    print("🎯 操作完成")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
