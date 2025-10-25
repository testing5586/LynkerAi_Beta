"""
真命盘验证系统 - 数据库表初始化
创建三张表：pending_charts（待审核）、verified_charts（已通过）、rejected_charts（已拒绝）
"""
import os
from supabase import create_client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("❌ 缺少 SUPABASE_URL 或 SUPABASE_KEY 环境变量")
    exit(1)

sp = create_client(url, key)

SQL = """
-- 待审核命盘表
CREATE TABLE IF NOT EXISTS public.pending_charts (
  id bigserial PRIMARY KEY,
  uploader_id bigint,
  raw_text text,
  parsed_json jsonb,
  source text default 'user_upload',
  status text default 'pending',
  created_at timestamptz default now()
);

-- 已验证通过的真命盘表
CREATE TABLE IF NOT EXISTS public.verified_charts (
  id bigserial PRIMARY KEY,
  pending_id bigint,
  name text,
  gender text,
  birth_time timestamptz,
  ziwei_palace text,
  main_star text,
  shen_palace text,
  birth_data jsonb,
  verify_score numeric,
  verified_by text default 'ai_pipeline',
  created_at timestamptz default now()
);

-- 已拒绝的命盘表
CREATE TABLE IF NOT EXISTS public.rejected_charts (
  id bigserial PRIMARY KEY,
  pending_id bigint,
  reason text,
  suggestion text,
  created_at timestamptz default now()
);
"""

print("🔧 开始创建验证系统数据库表...")
print("=" * 60)

try:
    # 使用 PostgreSQL execute_sql_tool 替代 RPC
    # Supabase Python SDK 不直接支持原始 SQL 执行
    # 我们需要使用 execute_sql_tool 或者逐个创建表
    print("⚠️  请使用 execute_sql_tool 执行以下 SQL：")
    print(SQL)
    print("=" * 60)
    print("✅ 表结构准备完成，请手动执行 SQL 或使用工具")
except Exception as e:
    print(f"❌ 创建表失败: {str(e)}")
    exit(1)
