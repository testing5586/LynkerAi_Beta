-- ============================================
-- AI Rules Table Schema
-- ============================================
-- 用途：存储 AI 模型配置规则
-- 包含：模型选择、训练间隔等全局参数

CREATE TABLE IF NOT EXISTS ai_rules (
    id BIGSERIAL PRIMARY KEY,
    rule_name TEXT NOT NULL UNIQUE,
    rule_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by TEXT
);

-- 插入默认配置
INSERT INTO ai_rules (rule_name, rule_value, description) VALUES
    ('MODEL_FREE', 'gpt-4o-mini', 'Free 用户使用的 AI 模型'),
    ('MODEL_PRO', 'gpt-4-turbo', 'Pro 用户使用的 AI 模型'),
    ('MODEL_MASTER', 'gpt-4-turbo', 'Superintendent Admin 使用的 AI 模型'),
    ('TRAINING_INTERVAL_DAYS', '7', 'Master AI 自动学习周期（天）')
ON CONFLICT (rule_name) DO NOTHING;

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_ai_rules_name ON ai_rules(rule_name);

-- 添加注释
COMMENT ON TABLE ai_rules IS 'AI 模型配置规则表';
COMMENT ON COLUMN ai_rules.rule_name IS '规则名称（唯一）';
COMMENT ON COLUMN ai_rules.rule_value IS '规则值';
COMMENT ON COLUMN ai_rules.description IS '规则描述';
COMMENT ON COLUMN ai_rules.updated_at IS '最后更新时间';
COMMENT ON COLUMN ai_rules.updated_by IS '更新人';
