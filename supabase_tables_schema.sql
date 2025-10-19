-- ============================================================
-- LynkerAI Supabase 数据表结构定义
-- ============================================================
-- 使用说明：在 Supabase Dashboard 的 SQL Editor 中执行此脚本
-- ============================================================

-- 1️⃣ 验证命盘记录表
CREATE TABLE IF NOT EXISTS verified_charts (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    chart_id VARCHAR(255) NOT NULL,
    score DECIMAL(5,3) NOT NULL,
    confidence VARCHAR(50),
    matched_keywords TEXT[],
    verified_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 为查询优化添加索引
CREATE INDEX IF NOT EXISTS idx_verified_charts_user_id ON verified_charts(user_id);
CREATE INDEX IF NOT EXISTS idx_verified_charts_chart_id ON verified_charts(chart_id);

-- 2️⃣ 人生事件权重学习表
CREATE TABLE IF NOT EXISTS life_event_weights (
    id BIGSERIAL PRIMARY KEY,
    event_desc TEXT NOT NULL,
    weight DECIMAL(5,2) DEFAULT 1.0,
    similarity DECIMAL(5,4),
    updated_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 使用 event_desc 作为唯一键（用于 upsert）
CREATE UNIQUE INDEX IF NOT EXISTS idx_life_event_weights_desc ON life_event_weights(event_desc);

-- 3️⃣ 用户人生标签表
CREATE TABLE IF NOT EXISTS user_life_tags (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL UNIQUE,
    career_type VARCHAR(255),
    marriage_status VARCHAR(100),
    children INTEGER DEFAULT 0,
    event_count INTEGER DEFAULT 0,
    updated_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 为查询优化添加索引
CREATE INDEX IF NOT EXISTS idx_user_life_tags_user_id ON user_life_tags(user_id);

-- 4️⃣ 同命匹配结果表
CREATE TABLE IF NOT EXISTS soulmate_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    matched_user_id TEXT NOT NULL,
    similarity NUMERIC(5,3),
    shared_tags JSONB,
    verified_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 为查询优化添加索引
CREATE INDEX IF NOT EXISTS idx_soulmate_matches_user_id ON soulmate_matches(user_id);
CREATE INDEX IF NOT EXISTS idx_soulmate_matches_matched_user_id ON soulmate_matches(matched_user_id);
CREATE INDEX IF NOT EXISTS idx_soulmate_matches_similarity ON soulmate_matches(similarity DESC);

-- 创建复合唯一索引，防止重复匹配记录
CREATE UNIQUE INDEX IF NOT EXISTS idx_soulmate_matches_unique 
ON soulmate_matches(user_id, matched_user_id);

-- ============================================================
-- 验证表是否创建成功
-- ============================================================
SELECT 
    tablename, 
    schemaname 
FROM pg_tables 
WHERE tablename IN ('verified_charts', 'life_event_weights', 'user_life_tags', 'soulmate_matches')
ORDER BY tablename;
