-- 创建真命盘验证日志表
-- 用于记录用户对AI命理断语的验证结果

CREATE TABLE IF NOT EXISTS public.truth_validation_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    chart_id TEXT NOT NULL,
    statement_id TEXT NOT NULL,
    ai_statement TEXT NOT NULL,
    user_choice BOOLEAN NOT NULL,
    ai_prediction BOOLEAN DEFAULT TRUE,
    match_result BOOLEAN NOT NULL,
    phase TEXT DEFAULT 'final_validation',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    trust_score FLOAT DEFAULT 0.0,
    source_ai TEXT DEFAULT 'Primary'
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_truth_validation_logs_user_id ON public.truth_validation_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_truth_validation_logs_chart_id ON public.truth_validation_logs(chart_id);
CREATE INDEX IF NOT EXISTS idx_truth_validation_logs_statement_id ON public.truth_validation_logs(statement_id);
CREATE INDEX IF NOT EXISTS idx_truth_validation_logs_timestamp ON public.truth_validation_logs(timestamp);

-- 添加表注释
COMMENT ON TABLE public.truth_validation_logs IS '真命盘验证日志表，记录用户对AI命理断语的验证结果';
COMMENT ON COLUMN public.truth_validation_logs.user_id IS '用户ID';
COMMENT ON COLUMN public.truth_validation_logs.chart_id IS '命盘ID';
COMMENT ON COLUMN public.truth_validation_logs.statement_id IS '断语唯一标识符';
COMMENT ON COLUMN public.truth_validation_logs.ai_statement IS 'AI生成的命理断语文本';
COMMENT ON COLUMN public.truth_validation_logs.user_choice IS '用户选择（True=准，False=不准）';
COMMENT ON COLUMN public.truth_validation_logs.ai_prediction IS 'AI预测结果（默认认为自己的断语准确）';
COMMENT ON COLUMN public.truth_validation_logs.match_result IS '匹配结果（用户选择与AI预测是否一致）';
COMMENT ON COLUMN public.truth_validation_logs.phase IS '验证阶段（如：final_validation, exploration等）';
COMMENT ON COLUMN public.truth_validation_logs.timestamp IS '验证时间戳';
COMMENT ON COLUMN public.truth_validation_logs.trust_score IS '信任分数（0-1之间）';
COMMENT ON COLUMN public.truth_validation_logs.source_ai IS 'AI来源（Primary, Child_Bazi, Child_Ziwei等）';

-- 启用行级安全性（RLS）
ALTER TABLE public.truth_validation_logs ENABLE ROW LEVEL SECURITY;

-- 创建RLS策略：用户只能查看自己的验证记录
CREATE POLICY "Users can view own validation logs" ON public.truth_validation_logs
    FOR SELECT USING (auth.uid()::text = user_id);

-- 创建RLS策略：用户只能插入自己的验证记录
CREATE POLICY "Users can insert own validation logs" ON public.truth_validation_logs
    FOR INSERT WITH CHECK (auth.uid()::text = user_id);

-- 创建RLS策略：用户只能更新自己的验证记录
CREATE POLICY "Users can update own validation logs" ON public.truth_validation_logs
    FOR UPDATE USING (auth.uid()::text = user_id);

-- 创建RLS策略：用户只能删除自己的验证记录
CREATE POLICY "Users can delete own validation logs" ON public.truth_validation_logs
    FOR DELETE USING (auth.uid()::text = user_id);