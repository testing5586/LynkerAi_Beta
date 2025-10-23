"""
🔍 LynkerAI Birthchart Database Health Checker
Version: 1.0
Author: Superintendent System
Purpose:
    检查 Supabase 数据库中 birthcharts 表结构与内容是否符合 Child AI 分析需求。
"""

from supabase import create_client
import os
import json

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ 环境变量缺失：请设置 SUPABASE_URL 与 SUPABASE_KEY。")
    exit()

client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("\n🧠 开始检测 birthcharts 数据表结构...\n")

# 检查 birth_data 字段是否存在
try:
    columns_res = client.rpc("pg_table_def", {"tablename": "birthcharts"}).execute()
    columns = [col["column_name"] for col in columns_res.data]
    if "birth_data" not in columns:
        print("⚠️ 未发现 'birth_data' 字段。Child AI 将无法解析命盘数据。")
        print("➡️ 请在 Supabase SQL 执行：ALTER TABLE public.birthcharts ADD COLUMN birth_data JSONB;")
        exit()
    else:
        print("✅ 已检测到 birth_data 字段。")
except Exception:
    print("⚠️ 无法直接检测字段结构（RPC未启用）。将通过查询验证。")

# 查询命盘数据
res = client.table("birthcharts").select("id, name, birth_data").limit(20).execute()
data = res.data

if not data:
    print("⚠️ 数据表为空，请插入命盘样本。")
    exit()
else:
    print(f"✅ 检测到 {len(data)} 条命盘记录。\n")

# 检查 JSON 字段完整性
valid_count = 0
missing = {"marriage_palace_star": 0, "wealth_palace_star": 0, "transformations": 0}

for row in data:
    birth_data = row.get("birth_data") or {}
    if not isinstance(birth_data, dict):
        print(f"⚠️ ID {row['id']} ({row['name']}) 的 birth_data 格式错误：不是 JSON 对象。")
        continue

    # 检查子字段
    missing_flag = False
    for key in missing.keys():
        if key not in birth_data:
            missing[key] += 1
            missing_flag = True

    if not missing_flag:
        valid_count += 1

# 输出总结报告
print("📊 字段完整性统计：")
for key, count in missing.items():
    print(f"  • {key}: {count} 条记录缺失")

print(f"\n✅ 完整 JSON 命盘: {valid_count} / {len(data)} 条\n")

if valid_count == 0:
    print("❌ 所有命盘缺少关键字段，Child AI 将进入 fallback 模式（“廉贞为主”）。")
elif valid_count < len(data) / 2:
    print("⚠️ 超过一半命盘数据缺失字段，Child AI 输出将不稳定。")
else:
    print("🎯 数据结构健康。Child AI 可正常执行化禄/化忌/宫位分析。")

print("\n✅ 检测完毕。\n")
