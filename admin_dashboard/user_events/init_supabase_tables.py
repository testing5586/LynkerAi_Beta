#!/usr/bin/env python3
"""
在 Supabase 云端初始化表
Initialize Tables in Supabase Cloud
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from admin_dashboard.user_events.supabase_client import get_client

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

def main():
    print("=" * 60)
    print("🔧 在 Supabase 云端初始化表")
    print("=" * 60)
    
    supabase = get_client()
    if not supabase:
        print("❌ Supabase 客户端初始化失败")
        return
    
    print("\n⚠️ Supabase Python SDK 不支持直接执行 SQL")
    print("请在 Supabase Dashboard 的 SQL Editor 中执行以下 SQL:\n")
    print("-" * 60)
    print(SQL_CREATE_TABLES)
    print("-" * 60)
    
    print("\n📝 步骤:")
    print("1. 访问 Supabase Dashboard: https://supabase.com/dashboard")
    print("2. 选择你的项目")
    print("3. 左侧菜单点击 'SQL Editor'")
    print("4. 创建新查询，粘贴上面的 SQL")
    print("5. 点击 'Run' 执行")
    
    print("\n✅ 执行完成后，重新运行测试: python user_events/test_system.py")

if __name__ == "__main__":
    main()
