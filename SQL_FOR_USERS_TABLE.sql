-- ============================================================
-- 为 public.users 表添加 Google Drive 绑定支持
-- ============================================================
-- 在 Supabase Dashboard 的 SQL Editor 中执行此脚本
-- ============================================================

-- 添加 Google Drive 相关字段
ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS drive_connected BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS drive_access_token TEXT,
ADD COLUMN IF NOT EXISTS drive_email TEXT;

-- 创建索引以优化查询性能
CREATE INDEX IF NOT EXISTS idx_users_drive_connected 
ON public.users(drive_connected);

CREATE INDEX IF NOT EXISTS idx_users_drive_email 
ON public.users(drive_email);

-- 验证字段是否添加成功
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'users' 
  AND column_name IN ('drive_connected', 'drive_access_token', 'drive_email')
ORDER BY column_name;

-- 预期输出：
-- drive_access_token | text    | YES | NULL
-- drive_connected    | boolean | YES | false
-- drive_email        | text    | YES | NULL
