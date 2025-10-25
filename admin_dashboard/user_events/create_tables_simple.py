#!/usr/bin/env python3
"""
通过 Supabase REST API 创建表
使用 SQL 视图方式（兜底方案：提供 SQL 给用户手动执行）
"""

import os

SQL_CREATE_TABLES = """-- 创建 user_events 表
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

def main():
    print("=" * 70)
    print("📋 Supabase 建表 SQL 脚本")
    print("=" * 70)
    
    supabase_url = os.getenv("SUPABASE_URL", "")
    
    if not supabase_url:
        print("❌ 未找到 SUPABASE_URL 环境变量")
        return
    
    project_id = supabase_url.replace("https://", "").replace(".supabase.co", "")
    dashboard_url = f"https://supabase.com/dashboard/project/{project_id}/sql/new"
    
    print("\n📝 请在 Supabase Dashboard 执行以下 SQL:\n")
    print("=" * 70)
    print(SQL_CREATE_TABLES)
    print("=" * 70)
    
    print("\n✅ 快速操作步骤:\n")
    print(f"1. 点击链接打开 SQL Editor:")
    print(f"   {dashboard_url}")
    print("\n2. 复制上面的 SQL 脚本")
    print("\n3. 粘贴到 SQL Editor")
    print("\n4. 点击 'Run' 按钮执行")
    print("\n5. 执行成功后，运行测试验证:")
    print("   cd admin_dashboard")
    print("   python user_events/test_system.py")
    
    print("\n" + "=" * 70)
    print("💡 提示: SQL 脚本已保存到此文件中，可随时查看")
    print("=" * 70)

if __name__ == "__main__":
    main()
