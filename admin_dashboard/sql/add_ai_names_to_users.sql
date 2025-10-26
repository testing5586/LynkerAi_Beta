-- 为 users 表添加AI名字字段
-- 支持用户自定义三个AI的名字

ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS primary_ai_name TEXT DEFAULT '灵伴',
ADD COLUMN IF NOT EXISTS bazi_child_name TEXT DEFAULT '八字观察员',
ADD COLUMN IF NOT EXISTS ziwei_child_name TEXT DEFAULT '星盘参谋';

COMMENT ON COLUMN public.users.primary_ai_name IS '主AI名字（温柔陪伴者）';
COMMENT ON COLUMN public.users.bazi_child_name IS '八字验证Child AI名字';
COMMENT ON COLUMN public.users.ziwei_child_name IS '紫微验证Child AI名字';
