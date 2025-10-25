#!/usr/bin/env python3
"""
直接在 Supabase 云端创建表
Create Tables Directly in Supabase Cloud via psycopg2
"""

import os
import sys

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("❌ psycopg2 未安装，正在安装...")
    os.system("pip install psycopg2-binary")
    import psycopg2
    from psycopg2 import sql

SQL_CREATE_TABLES = """
-- 创建 user_events 表
CREATE TABLE IF NOT EXISTS public.user_events (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  event_type TEXT NOT NULL,
  event_payload JSONB DEFAULT '{}'::jsonb,
  emotion_label TEXT,
  emotion_score NUMERIC(4,3),
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 创建 user_insights 表
CREATE TABLE IF NOT EXISTS public.user_insights (
  user_id BIGINT PRIMARY KEY,
  top_concerns TEXT[] DEFAULT '{}',
  emotion_tendency TEXT DEFAULT 'neutral',
  last_7d_event_count INT DEFAULT 0,
  push_ready BOOLEAN DEFAULT FALSE,
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- 启用 RLS
ALTER TABLE public.user_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_insights ENABLE ROW LEVEL SECURITY;

-- 删除旧策略（如果存在）
DROP POLICY IF EXISTS p_user_events_all ON public.user_events;
DROP POLICY IF EXISTS p_user_insights_all ON public.user_insights;

-- 创建策略（允许所有操作）
CREATE POLICY p_user_events_all ON public.user_events FOR ALL
  USING (true)
  WITH CHECK (true);

CREATE POLICY p_user_insights_all ON public.user_insights FOR ALL
  USING (true)
  WITH CHECK (true);
"""

def get_supabase_connection_string():
    """从环境变量构建 Supabase PostgreSQL 连接字符串"""
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_KEY", "")
    
    if not supabase_url:
        return None
    
    # Supabase URL 格式: https://xxxxx.supabase.co
    # PostgreSQL 格式: postgresql://postgres.xxxxx:password@aws-0-region.pooler.supabase.com:6543/postgres
    
    # 提取项目 ID
    project_id = supabase_url.replace("https://", "").replace(".supabase.co", "")
    
    # Supabase 连接池端口通常是 6543
    # 直接连接端口是 5432，但推荐使用连接池
    
    # 尝试多种格式
    possible_formats = [
        f"postgresql://postgres:{supabase_key}@db.{project_id}.supabase.co:5432/postgres",
        f"postgresql://postgres.{project_id}:{supabase_key}@aws-0-us-west-1.pooler.supabase.com:6543/postgres",
    ]
    
    return possible_formats

def main():
    print("=" * 60)
    print("🔧 在 Supabase 云端创建表")
    print("=" * 60)
    
    connection_strings = get_supabase_connection_string()
    
    if not connection_strings:
        print("❌ 未找到 SUPABASE_URL 环境变量")
        print("请确保在 Replit Secrets 中配置了 SUPABASE_URL 和 SUPABASE_KEY")
        return
    
    conn = None
    success = False
    
    # 尝试多种连接方式
    for conn_str in connection_strings:
        try:
            print(f"\n🔌 尝试连接 Supabase PostgreSQL...")
            conn = psycopg2.connect(conn_str)
            print("✅ 连接成功！")
            success = True
            break
        except Exception as e:
            print(f"⚠️ 连接失败（尝试下一种格式）: {e}")
            continue
    
    if not success:
        print("\n" + "=" * 60)
        print("❌ 所有连接尝试失败")
        print("\n📝 请手动在 Supabase Dashboard 执行 SQL:")
        print("=" * 60)
        print(SQL_CREATE_TABLES)
        print("=" * 60)
        print("\n步骤:")
        print("1. 访问 https://supabase.com/dashboard")
        print("2. 选择项目 → SQL Editor")
        print("3. 粘贴上面的 SQL → Run")
        return
    
    try:
        cur = conn.cursor()
        
        print("\n📝 执行建表 SQL...")
        cur.execute(SQL_CREATE_TABLES)
        conn.commit()
        
        print("✅ 表创建成功！")
        
        # 验证表是否存在
        print("\n🔍 验证表结构...")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('user_events', 'user_insights')
        """)
        
        tables = cur.fetchall()
        for table in tables:
            print(f"  ✓ {table[0]}")
        
        if len(tables) == 2:
            print("\n🎉 Supabase 表创建完成！")
            print("\n下一步: 运行测试验收")
            print("  cd admin_dashboard")
            print("  python user_events/test_system.py")
        else:
            print(f"\n⚠️ 只创建了 {len(tables)}/2 张表")
        
        cur.close()
        
    except Exception as e:
        print(f"❌ 执行 SQL 失败: {e}")
        print("\n请手动在 Supabase Dashboard 执行上述 SQL")
        if conn:
            conn.rollback()
    
    finally:
        if conn:
            conn.close()
            print("\n🔌 数据库连接已关闭")

if __name__ == "__main__":
    main()
