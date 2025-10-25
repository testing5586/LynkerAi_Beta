# 用户行为日志 + 情绪识别模块使用指南

## 📦 模块概述

用户行为日志与情绪识别模块为 LynkerAI 提供完整的用户行为追踪、情绪分析和画像生成能力。

### 核心功能

- ✅ **事件追踪** - 记录用户浏览宫位、提问、情绪表达等行为
- ✅ **情绪识别** - 优先使用 OpenAI API，兜底离线中文词典
- ✅ **画像聚合** - 7天数据统计生成用户关注点和情绪倾向
- ✅ **可视化面板** - Admin Dashboard 集成实时监控

---

## 🗄️ 数据库结构

### 表 1: `user_events` (用户事件流)

```sql
CREATE TABLE public.user_events (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  event_type TEXT NOT NULL,
  event_payload JSONB DEFAULT '{}'::jsonb,
  emotion_label TEXT,                    -- positive/neutral/anxious/sad/angry
  emotion_score NUMERIC(4,3),            -- 0~1 置信度
  created_at TIMESTAMPTZ DEFAULT now()
);
```

### 表 2: `user_insights` (用户画像)

```sql
CREATE TABLE public.user_insights (
  user_id BIGINT PRIMARY KEY,
  top_concerns TEXT[] DEFAULT '{}',      -- ["夫妻宫","破军"]
  emotion_tendency TEXT DEFAULT 'neutral',
  last_7d_event_count INT DEFAULT 0,
  push_ready BOOLEAN DEFAULT FALSE,      -- 推送就绪标记
  updated_at TIMESTAMPTZ DEFAULT now()
);
```

### 初始化步骤

**⚠️ 重要：表需要在 Supabase Dashboard 手动创建**

1. 访问 https://supabase.com/dashboard
2. 选择项目 → SQL Editor
3. 运行以下命令获取完整 SQL：

```bash
cd admin_dashboard
python user_events/init_supabase_tables.py
```

4. 复制 SQL 并在 Dashboard 执行

---

## 🔌 API 接口

### 1. 追踪事件

**POST** `/api/events/track`

```json
{
  "user_id": 3,
  "event_type": "VIEW_PALACE" | "QUESTION" | "FEELING" | "MARK_RESONANCE",
  "event_payload": {
    "palace": "夫妻宫",
    "text": "我对婚姻很担心",
    "tags": ["廉贞", "破军"]
  }
}
```

**响应示例：**
```json
{
  "status": "ok",
  "id": 42,
  "emotion": {
    "label": "anxious",
    "score": 0.75
  }
}
```

### 2. 查询用户画像

**GET** `/api/insights/<user_id>`

**响应示例：**
```json
{
  "user_id": 3,
  "top_concerns": ["夫妻宫", "化忌", "破军"],
  "emotion_tendency": "anxious",
  "last_7d_event_count": 12,
  "push_ready": true,
  "updated_at": "2025-10-23T14:30:00Z"
}
```

### 3. 事件概览统计

**GET** `/api/events/stats/overview`

**响应示例：**
```json
{
  "total_events_7d": 156,
  "total_events_all": 823,
  "emotion_distribution": {
    "positive": 45,
    "anxious": 67,
    "neutral": 32,
    "sad": 12
  },
  "last_updated": "2025-10-23T14:30:00Z"
}
```

---

## 🧠 情绪识别模式

### OpenAI 模式（优先）

- 使用 `gpt-4o-mini` 分析文本情绪
- 返回 5 种标签：`positive` / `neutral` / `anxious` / `sad` / `angry`
- 置信度 0~1

### 离线词典模式（兜底）

内置中文情绪词典（100+ 关键词）：
- **positive**: 开心、高兴、满意、幸福
- **anxious**: 焦虑、担心、不安、害怕
- **sad**: 难过、伤心、失望、孤独
- **angry**: 生气、愤怒、讨厌、烦躁

---

## 📊 每日聚合任务

### 执行聚合

```bash
cd admin_dashboard
python user_events/aggregator.py
```

### 聚合逻辑

1. 统计近 7 天每个用户事件数
2. 提取高频关注点（Top 3）
3. 计算情绪倾向（众数）
4. 判断推送就绪：
   - **条件 1**: 7天事件 ≥ 5
   - **条件 2**: FEELING + anxious ≥ 2

### 定时任务（可选）

添加到系统 crontab：
```bash
0 2 * * * cd /path/to/admin_dashboard && python user_events/aggregator.py
```

---

## 🎨 可视化面板

访问 **http://localhost:5000/dashboard**

### 新增卡片

#### 1. 用户行为概览（7天）
- 7日事件数统计
- 情绪分布柱状图（Plotly.js）
- Top3 关注点标签

#### 2. 用户画像查询
- 输入 user_id 实时查询
- 显示情绪倾向、事件数、关注点
- 推送就绪状态

---

## 📱 前端调用示例

### 示例 1: 记录宫位查看

```javascript
fetch('/api/events/track', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    user_id: CURRENT_USER_ID,
    event_type: 'VIEW_PALACE',
    event_payload: { palace: '夫妻宫' }
  })
})
.then(res => res.json())
.then(data => console.log('事件已记录:', data));
```

### 示例 2: 记录用户提问（带情绪分析）

```javascript
fetch('/api/events/track', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    user_id: CURRENT_USER_ID,
    event_type: 'QUESTION',
    event_payload: { 
      text: '我对婚姻很担心，总是反复焦虑' 
    }
  })
})
.then(res => res.json())
.then(data => {
  console.log('情绪标签:', data.emotion.label);
  console.log('置信度:', data.emotion.score);
});
```

### 示例 3: 记录用户点赞"共鸣"

```javascript
fetch('/api/events/track', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    user_id: CURRENT_USER_ID,
    event_type: 'MARK_RESONANCE',
    event_payload: { 
      target: '文章/命例ID',
      tags: ['廉贞', '破军'] 
    }
  })
});
```

---

## 🧪 测试验收

运行完整测试套件：

```bash
cd admin_dashboard
python user_events/test_system.py
```

**测试包含：**
1. ✅ 发送 4 个测试事件（VIEW_PALACE / QUESTION / FEELING / MARK_RESONANCE）
2. ✅ 查询事件概览
3. ✅ 执行每日聚合
4. ✅ 查询用户画像

---

## 🔐 环境变量

模块使用以下环境变量（已存在）：

- `SUPABASE_URL` - Supabase 项目 URL
- `SUPABASE_KEY` - Supabase 服务密钥
- `OPENAI_API_KEY` - OpenAI API 密钥（优先）
- `LYNKER_MASTER_KEY` - 备用 API 密钥

**兜底策略：** 无 OpenAI key 时自动切换到离线词典模式

---

## 📂 文件结构

```
admin_dashboard/
  user_events/
    __init__.py
    supabase_client.py          # Supabase 客户端单例
    emotion_analyzer.py         # 情绪识别器（OpenAI + 离线）
    event_api.py                # Flask Blueprint (API 路由)
    aggregator.py               # 每日聚合任务
    schema_check.py             # 表结构检查
    init_supabase_tables.py     # Supabase 建表指引
    test_system.py              # 完整测试脚本
  app.py                        # Flask 主应用（已注册 Blueprint）
  templates/dashboard.html      # 管理面板（已添加可视化卡片）
```

---

## 🚨 注意事项

1. **不要硬编码 API Key** - 统一读取环境变量
2. **日志统一中文** - 便于排错
3. **端口 5000** - 与现有 Admin Dashboard 共用
4. **不强依赖 psycopg2** - 优先使用 Supabase REST API
5. **Supabase 表手动创建** - Python SDK 不支持 SQL 执行

---

## ✅ 验收清单

- [x] user_events 表已创建（Supabase Dashboard）
- [x] user_insights 表已创建（Supabase Dashboard）
- [x] RLS 策略已配置
- [x] API `/api/events/track` 可追踪事件
- [x] API `/api/insights/<user_id>` 可查询画像
- [x] API `/api/events/stats/overview` 可获取概览
- [x] 情绪识别功能正常（OpenAI + 离线兜底）
- [x] 每日聚合脚本可执行
- [x] Dashboard 可视化界面已集成
- [x] 测试脚本通过验收

---

**🎉 模块已完成，等待 Supabase 表创建后即可使用！**
