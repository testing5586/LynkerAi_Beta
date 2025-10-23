# 🧠 Master AI 登录触发推理系统使用指南

## 📌 功能概述

当用户登录时，系统自动触发 **Master AI Reasoner 推理引擎**，为用户生成个性化预测，并根据置信度自动刷新"同命推荐榜"。

---

## 🚀 核心功能

1. **自动推理预测**
   - 调用 `master_ai_reasoner.reason_user(user_id)`
   - 基于命盘、匹配记录、用户反馈生成多源预测
   - 预测结果自动存入 `predictions` 表
   - 高置信度洞察加密存入 Master Vault

2. **智能推荐榜刷新**
   - **触发条件**：预测置信度 ≥ 0.6
   - **自动更新**：`recommendations` 表的 Top 10 同命推荐
   - **双边计算**：使用改进的匹配算法
   
3. **完整日志记录**
   - 路径：`logs/user_login_activity.log`
   - 包含：时间戳、用户 ID、置信度、刷新状态

---

## 🔌 API 接口

### POST /login_refresh_ai

**功能**：用户登录触发 Master AI 推理引擎

**请求示例**：
```bash
curl -X POST http://localhost:5000/login_refresh_ai \
  -H "Content-Type: application/json" \
  -d '{"user_id": 2}'
```

**请求参数**：
```json
{
  "user_id": 2
}
```

**响应示例**：
```json
{
  "status": "ok",
  "user_id": 2,
  "prediction": {
    "user_id": 2,
    "user_name": "命主A",
    "pair": "巳-天府",
    "confidence": 0.58,
    "time_window": "未来 6-12 个月",
    "traits": ["性格显著", "缘分佳", "行动力强", "后劲强"],
    "evidence": {
      "population_count": 1,
      "population_ratio": 0.1667,
      "adjusted_confidence": 0.5,
      "match_success_rate": 1.0,
      "avg_feedback_score": 0,
      "data_sources": {
        "birthcharts": 1,
        "match_results": 5,
        "feedback": 0
      },
      "signals": [
        "主星/命宫组合统计",
        "身宫一致加成",
        "匹配数据 (5 条)"
      ]
    }
  },
  "refreshed": false,
  "refresh_count": 0,
  "recommendations": []
}
```

**响应字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 请求状态（"ok" 或 "error"） |
| `user_id` | int | 用户 ID |
| `prediction` | object | AI 预测结果 |
| `prediction.confidence` | float | 预测置信度 (0-1) |
| `prediction.traits` | array | 性格特质标签 |
| `prediction.evidence` | object | 推理证据（包含数据源详情） |
| `refreshed` | boolean | 是否触发推荐榜刷新 |
| `refresh_count` | int | 更新的推荐记录数 |
| `recommendations` | array | Top 10 推荐列表 |

---

## 📊 工作流程

```
用户登录
  ↓
触发 /login_refresh_ai
  ↓
调用 master_ai_reasoner.reason_user(user_id)
  ↓
生成 AI 预测（整合命盘 + 匹配 + 反馈）
  ↓
预测存入 predictions 表
  ↓
高置信度洞察 (≥ 0.5) 加密存入 Master Vault
  ↓
判断：置信度 ≥ 0.6？
  ├─ 是 → 刷新 recommendations 表
  └─ 否 → 跳过刷新
  ↓
返回预测 + Top 10 推荐榜
  ↓
记录日志到 logs/user_login_activity.log
```

---

## 📝 日志示例

```log
[2025-10-23 10:59:08] 🔔 用户 2 登录触发推理引擎...
[2025-10-23 10:59:15] ✅ 登录结果: user=2, conf=0.58, refreshed=False, top10_count=0

[2025-10-23 10:59:32] 🔔 用户 4 登录触发推理引擎...
[2025-10-23 10:59:37] ✅ 用户 4 推理置信度高(0.667)，刷新推荐榜...
[2025-10-23 10:59:38] 📊 已更新 0 条推荐记录
[2025-10-23 10:59:38] ✅ 登录结果: user=4, conf=0.667, refreshed=True, top10_count=0
```

---

## 🔐 权限控制

- **普通用户**：使用自己的 AI Provider（free tier）
- **Master AI / Superintendent Admin**：使用 Lynker 主 Key
- **按需触发**：仅在用户登录时运行，不做后台循环（节省 token）

---

## 💡 使用场景

1. **用户登录时自动生成预测**
   - 无需手动调用 API
   - 登录即触发智能分析

2. **高置信度自动刷新推荐**
   - 置信度 ≥ 0.6 时自动更新同命推荐榜
   - 提供最新、最准确的匹配结果

3. **完整审计追踪**
   - 每次触发都有日志记录
   - 便于分析和优化

---

## 🛠️ 技术细节

### 数据库表

1. **predictions** - 预测结果存储
```sql
CREATE TABLE predictions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    user_name TEXT,
    pair TEXT,
    traits JSONB,
    time_window TEXT,
    confidence NUMERIC,
    evidence JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT predictions_user_pair_unique UNIQUE (user_id, pair)
);
```

2. **recommendations** - 推荐榜存储
```sql
CREATE TABLE recommendations (
    user_a_id BIGINT,
    user_a_name TEXT,
    user_b_id BIGINT,
    user_b_name TEXT,
    match_score NUMERIC,
    matching_fields JSONB,
    created_at TIMESTAMPTZ
);
```

### Master Vault 集成

- 高置信度预测 (confidence ≥ 0.5) 自动加密存储
- 使用 AES256 加密
- 仅 Superintendent Admin 可解密
- 完整审计追踪

---

## ✅ 测试验证

**测试脚本**：
```bash
# 测试低置信度用户（不触发刷新）
curl -X POST http://localhost:5000/login_refresh_ai \
  -H "Content-Type: application/json" \
  -d '{"user_id": 2}'

# 测试高置信度用户（触发刷新）
curl -X POST http://localhost:5000/login_refresh_ai \
  -H "Content-Type: application/json" \
  -d '{"user_id": 4}'

# 查看日志
cat logs/user_login_activity.log
```

---

## 🎯 下一步优化建议

1. **实时通知**：推送高置信度预测给用户
2. **A/B 测试**：对比自动刷新 vs 手动刷新的用户体验
3. **性能监控**：记录响应时间和资源消耗
4. **智能缓存**：避免短时间内重复计算

---

**文档版本**：1.0  
**最后更新**：2025-10-23  
**维护者**：LynkerAI Team
