# 三方AI智能协作引擎 v2.0 使用指南

## 📖 概述

**Lynker Engine v2.0** 是 LynkerAI 的核心智能协作引擎，通过三层 AI Agent 架构实现真实的任务分解、数据分析和推理决策。

---

## 🧩 系统架构

### 三层AI协作体系

```
用户查询
    ↓
🤖 Child AI (执行分析层)
    ├── 数据库检索（birthcharts, match_results）
    ├── 命盘模式识别（高频主星、宫位组合）
    └── 统计规律提取
    ↓
🧩 Group Leader (任务协调层)
    ├── 任务分解
    ├── 结果整合
    └── 向 Master AI 汇报
    ↓
🧠 Master AI (主控推理层)
    ├── 综合分析（Vault + Supabase + 反馈）
    ├── 深度推理
    └── 最终决策与建议
```

---

## 📁 文件结构

```
admin_dashboard/
├── config.json                     # AI 引擎配置文件
├── lynker_engine.py                # 核心协作引擎
├── chat_hub_v2.py                  # Flask 接口层
├── ai_agents/
│   ├── __init__.py
│   ├── child_agent.py              # 执行分析层
│   ├── group_leader_agent.py       # 任务协调层
│   └── master_agent.py             # 主控推理层
├── app.py                          # Flask 主应用（已更新）
└── templates/
    └── chatroom.html               # 增强版聊天室界面
```

---

## 🚀 快速开始

### 1. 访问 AI 协作聊天室

```bash
https://[your-replit-url]/chatroom
```

### 2. 登录

使用 Superintendent Admin 令牌登录（参考 `ADMIN_DASHBOARD_GUIDE.md`）

### 3. 开始提问

**示例查询**：

```
📌 分析命盘数据库的高频组合
📌 统计武曲主星的婚姻规律
📌 查询天府坐巳的命盘特征
📌 推理紫微命宫的职业倾向
```

---

## 🔧 AI Agent 配置

### config.json 配置说明

```json
{
  "agents": {
    "master": {
      "model": "gpt-4-turbo",        // 主控推理模型
      "temperature": 0.7,             // 创造性推理
      "max_tokens": 800               // 详细结论
    },
    "leader": {
      "model": "gpt-4o-mini",         // 任务协调模型
      "temperature": 0.5,             // 平衡协调
      "max_tokens": 500
    },
    "child": {
      "model": "gpt-4o-mini",         // 执行分析模型
      "temperature": 0.3,             // 精确分析
      "max_tokens": 400
    }
  }
}
```

---

## 🎯 核心功能

### 1. Child AI - 执行分析

**职责**：
- ✅ 查询 Supabase 数据库（`birthcharts`, `match_results`）
- ✅ 识别高频命盘模式（主星、宫位、组合）
- ✅ 统计规律提取
- ✅ 生成数据驱动的初步总结

**方法**：
```python
child_agent.query_birthcharts(filters={"main_star": "天府"})
child_agent.analyze_pattern(task="查询命盘高频组合")
```

---

### 2. Group Leader - 任务协调

**职责**：
- ✅ 将用户查询分解为子任务
- ✅ 分配任务给 Child AI
- ✅ 整合 Child AI 的分析结果
- ✅ 向 Master AI 提供清晰汇报

**方法**：
```python
leader_agent.decompose_task(user_query)
leader_agent.coordinate(user_query, child_results)
```

---

### 3. Master AI - 主控推理

**职责**：
- ✅ 综合 Group Leader 汇报
- ✅ 引入 Master Vault 知识库
- ✅ 深度推理与模式发现
- ✅ 提供最终结论与建议

**方法**：
```python
master_agent.reason(user_query, leader_report, vault_context)
master_agent.synthesize_knowledge(findings)
```

---

## 🔄 工作流示例

### 用户查询："分析命盘数据库的高频组合"

#### Step 1: Child AI 执行分析
```
🤖 Child AI: 数据库共856个命盘，主星以天府为主，命宫多见巳宫。
高频组合：巳-天府(82例)、午-武曲(61例)、卯-紫微(47例)。
```

#### Step 2: Group Leader 协调整合
```
🧩 Group Leader: 已收集1项分析结果。
数据显示巳-天府组合占比最高(9.6%)，与传统命理稳重特质相符，
建议进一步验证其婚姻与职业倾向。
```

#### Step 3: Master AI 推理决策
```
🧠 Master AI: 基于数据分析和 Vault 知识库，巳-天府组合确实展现
"后劲强、婚姻晚成"特征，建议将此规律存入 Master Vault（置信度0.82），
并推荐用于匹配系统的权重调优。
```

---

## 🛡️ 安全与权限

### 环境变量要求

| 变量名 | 必需 | 说明 |
|--------|------|------|
| `MASTER_VAULT_KEY` | ✅ | AES256 加密密钥 & Flask Session |
| `OPENAI_API_KEY` | ✅ | OpenAI API（普通用户） |
| `LYNKER_MASTER_KEY` | ✅ | Master AI 专用 API Key |
| `SUPABASE_URL` | ⚠️ | Supabase 数据库（可选） |
| `SUPABASE_KEY` | ⚠️ | Supabase 密钥（可选） |

### 降级机制

当依赖不可用时，系统自动降级：

```
❌ Supabase 不可用 → 使用模拟数据
❌ OpenAI 不可用 → 使用简单文本总结
❌ Vault 不可用 → 跳过知识库引用
```

---

## 📊 集成现有系统

### 与 Master Vault Engine 集成

```python
# lynker_engine.py 中的 Vault 集成
from master_vault_engine import list_vault_entries

vault_context = self._get_vault_context(query)
master_response = self.master.process(query, leader_report, vault_context)
```

### 与 Multi-Model Dispatcher 集成

```python
# 自动选择模型（未来扩展）
from multi_model_dispatcher import get_model_for_user

model = get_model_for_user(user_id)
```

---

## 🐛 故障排查

### 问题：Child AI 无法查询数据库

**解决方案**：
1. 检查 `SUPABASE_URL` 和 `SUPABASE_KEY`
2. 查看日志：`logs/Admin_Dashboard_*.log`
3. 测试连接：
```python
python -c "from admin_dashboard.ai_agents.child_agent import ChildAgent; import json; config = json.load(open('admin_dashboard/config.json')); agent = ChildAgent(config); print(agent.query_birthcharts())"
```

### 问题：Master AI 推理失败

**解决方案**：
1. 检查 `LYNKER_MASTER_KEY` 或 `OPENAI_API_KEY`
2. 查看 API 配额余额
3. 降级到简单推理模式

### 问题：Socket.IO 连接断开

**解决方案**：
1. 检查 Flask-SocketIO 安装
2. 重启 workflow：
```bash
cd admin_dashboard && python app.py
```
3. 浏览器开发者工具查看 WebSocket 连接

---

## 📈 性能优化

### 1. 数据库查询缓存

```json
{
  "database": {
    "cache_ttl_seconds": 300
  }
}
```

### 2. AI 响应超时控制

```json
{
  "ai_collaboration": {
    "timeout_seconds": 30,
    "max_retries": 3
  }
}
```

### 3. Token 消耗优化

- Child AI: 400 tokens（精确分析）
- Leader: 500 tokens（平衡协调）
- Master AI: 800 tokens（详细推理）

---

## 🔮 未来扩展

### 计划功能

- [ ] **多用户并发支持** - 每个用户独立会话
- [ ] **历史对话存储** - Supabase `ai_conversations` 表
- [ ] **自定义 Agent 配置** - 用户可调整温度和模型
- [ ] **实时 Vault 更新** - 自动加密高置信度发现
- [ ] **可视化推理过程** - 显示 AI 思考链路

---

## 🎓 最佳实践

### 1. 提问技巧

✅ **明确具体**
```
❌ "分析命盘"
✅ "分析天府主星的婚姻规律"
```

✅ **包含上下文**
```
❌ "统计数据"
✅ "统计武曲守财局的高收入比例"
```

### 2. 解读结果

- **Child AI** → 数据事实（what）
- **Group Leader** → 关联发现（how）
- **Master AI** → 深度洞察（why）

### 3. 验证建议

Master AI 的建议应结合：
- 📊 统计数据（Child AI）
- 📚 Vault 知识（历史规律）
- 🧪 实际反馈（用户验证）

---

## 📞 技术支持

遇到问题？查看以下资源：

- 📖 **Admin Dashboard 文档**: `ADMIN_DASHBOARD_GUIDE.md`
- 📖 **Master Vault 文档**: `master_ai/MASTER_VAULT_ENGINE_GUIDE.md`
- 📖 **Reasoner 文档**: `master_ai/MASTER_AI_REASONER_GUIDE.md`
- 📝 **系统日志**: `logs/Admin_Dashboard_*.log`

---

## ✨ 总结

**Lynker Engine v2.0** 将模拟系统升级为真实的三方 AI 协作引擎：

- ✅ 真实数据库查询（Supabase）
- ✅ 真实 AI 推理（OpenAI GPT-4/4o-mini）
- ✅ 真实知识整合（Master Vault）
- ✅ 实时 WebSocket 通信（Socket.IO）
- ✅ 安全访问控制（SHA256 + Session）

**立即体验**: `https://[your-replit-url]/chatroom` 🚀
