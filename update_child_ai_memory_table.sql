-- ============================================================
-- 更新 child_ai_memory 表结构 - 添加缺失的列
-- ============================================================

-- 添加 interaction_count 列（如果不存在）
ALTER TABLE public.child_ai_memory 
ADD COLUMN IF NOT EXISTS interaction_count INTEGER DEFAULT 1;

-- 添加 last_interaction 列（如果不存在）
ALTER TABLE public.child_ai_memory 
ADD COLUMN IF NOT EXISTS last_interaction TIMESTAMP DEFAULT NOW();

-- 添加 summary 列（如果不存在）
ALTER TABLE public.child_ai_memory 
ADD COLUMN IF NOT EXISTS summary TEXT;

-- 添加 tags 列（如果不存在）
ALTER TABLE public.child_ai_memory 
ADD COLUMN IF NOT EXISTS tags TEXT[];

-- 添加 similarity 列（如果不存在）
ALTER TABLE public.child_ai_memory 
ADD COLUMN IF NOT EXISTS similarity FLOAT;

-- 创建索引（如果不存在）
CREATE INDEX IF NOT EXISTS idx_child_ai_memory_last_interaction 
ON public.child_ai_memory(last_interaction DESC);

-- 验证表结构
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'child_ai_memory'
ORDER BY ordinal_position;
