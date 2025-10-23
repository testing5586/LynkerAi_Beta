# 🤖 Multi-Model Dispatcher 使用指南

## 📌 功能概述

`multi_model_dispatcher.py` 是 LynkerAI 的智能模型分发系统，根据用户等级自动选择最合适的 AI 模型和 API Key。

---

## 🎯 核心功能

### 1️⃣ **自动模型选择** (`get_model_for_user`)

根据用户身份自动匹配 AI 模型：

| 用户等级 | AI Provider | 使用模型 | 配置键 |
|---------|------------|---------|--------|
| **Superintendent Admin** | - | `MODEL_MASTER` | `gpt-4-turbo` |
| **Pro 用户** | `pro` | `MODEL_PRO` | `gpt-4-turbo` |
| **Free 用户** | `free` / 未设置 | `MODEL_FREE` | `gpt-4o-mini` |

### 2️⃣ **智能 API Key 分发** (`get_api_key_for_user`)

根据用户身份选择 API Key：

| 用户身份 | API Key | 来源 |
|---------|---------|------|
| **Superintendent Admin** | `LYNKER_MASTER_KEY` | Replit Secrets |
| **普通用户** | `OPENAI_API_KEY` | Replit Secrets |

### 3️⃣ **动态配置加载** (`load_ai_rules`)

从 Supabase `ai_rules` 表动态加载配置，支持热更新，无需重启系统。

---

## 🗄️ 数据库 Schema

### `ai_rules` 表

```sql
CREATE TABLE ai_rules (
    id BIGSERIAL PRIMARY KEY,
    rule_name TEXT NOT NULL UNIQUE,
    rule_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by TEXT
);
```

### 默认配置

| rule_name | rule_value | description |
|-----------|-----------|-------------|
| `MODEL_FREE` | `gpt-4o-mini` | Free 用户使用的模型 |
| `MODEL_PRO` | `gpt-4-turbo` | Pro 用户使用的模型 |
| `MODEL_MASTER` | `gpt-4-turbo` | Superintendent Admin 使用的模型 |
| `TRAINING_INTERVAL_DAYS` | `7` | Master AI 自动学习周期（天） |

---

## 💻 使用示例

### 基础使用

```python
from multi_model_dispatcher import get_model_for_user, get_api_key_for_user

# 获取用户的 AI 模型
user_id = 2
model = get_model_for_user(user_id)
print(f"用户 {user_id} 使用模型: {model}")

# 获取用户的 API Key
api_key = get_api_key_for_user(user_id)
print(f"API Key: {api_key[:10]}...")
```

### 集成到 OpenAI 调用

```python
import openai
from multi_model_dispatcher import get_model_for_user, get_api_key_for_user

def call_ai_for_user(user_id: int, prompt: str):
    """为指定用户调用 AI，自动选择模型和 Key"""
    model = get_model_for_user(user_id)
    api_key = get_api_key_for_user(user_id)
    
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content
```

### 集成到 Master AI Reasoner

```python
from multi_model_dispatcher import get_model_for_user, get_api_key_for_user
import openai

def reason_user(user_id: int):
    """使用用户对应的模型进行推理"""
    model = get_model_for_user(user_id)
    api_key = get_api_key_for_user(user_id)
    
    client = openai.OpenAI(api_key=api_key)
    
    # 推理逻辑...
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是 Master AI 推理引擎..."},
            {"role": "user", "content": f"分析用户 {user_id} 的命盘..."}
        ]
    )
    
    return response.choices[0].message.content
```

---

## 🔧 配置管理

### 查看当前配置

```python
from multi_model_dispatcher import load_ai_rules

rules = load_ai_rules()
print("当前 AI 规则配置:")
for key, value in rules.items():
    print(f"  {key}: {value}")
```

### 更新配置（通过 Supabase）

```python
from supabase import create_client
import os

client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# 更新 Free 用户模型为 gpt-3.5-turbo
client.table("ai_rules").update({
    "rule_value": "gpt-3.5-turbo",
    "updated_at": "now()",
    "updated_by": "admin"
}).eq("rule_name", "MODEL_FREE").execute()

print("✅ 配置已更新！")
```

### 添加新规则

```python
client.table("ai_rules").insert({
    "rule_name": "MAX_TOKENS",
    "rule_value": "2000",
    "description": "AI 响应最大 token 数"
}).execute()
```

---

## 🧪 测试

### 运行测试

```bash
python multi_model_dispatcher.py
```

### 测试输出示例

```
=== Multi-Model Dispatcher 测试 ===

📋 AI 规则配置:
  MODEL_FREE: gpt-4o-mini
  MODEL_PRO: gpt-4-turbo
  MODEL_MASTER: gpt-4-turbo
  TRAINING_INTERVAL_DAYS: 7

🧪 测试用户模型选择:
🆓 用户 1 (Free) → 使用 gpt-4o-mini
👑 用户 2 (Superintendent Admin) → 使用 gpt-4-turbo
💎 用户 3 (Pro) → 使用 gpt-4-turbo
```

---

## 🔐 安全机制

### 1. **Secrets 管理**
- 所有 API Key 存储在 Replit Secrets 中
- 使用 `os.getenv()` 安全读取
- 永不在代码中硬编码密钥

### 2. **权限隔离**
- Superintendent Admin 使用 `LYNKER_MASTER_KEY`（Lynker 账户）
- 普通用户使用 `OPENAI_API_KEY`（用户自己的账户）
- 防止滥用和 token 超额

### 3. **降级保护**
- Supabase 连接失败时自动使用默认配置
- 用户不存在时默认使用 Free 模型
- 确保系统稳定性

---

## 📊 工作流程

```
用户发起 AI 请求
  ↓
调用 get_model_for_user(user_id)
  ↓
查询 users 表 → 获取 role & ai_provider
  ↓
查询 ai_rules 表 → 加载模型配置
  ↓
匹配规则:
  ├─ Superintendent Admin → MODEL_MASTER
  ├─ Pro 用户 → MODEL_PRO
  └─ Free 用户 → MODEL_FREE
  ↓
调用 get_api_key_for_user(user_id)
  ↓
  ├─ Superintendent Admin → LYNKER_MASTER_KEY
  └─ 普通用户 → OPENAI_API_KEY
  ↓
使用选定模型和 Key 调用 OpenAI API
  ↓
返回 AI 响应
```

---

## 🚀 集成示例

### 集成到 Flask API

```python
from flask import Flask, request, jsonify
from multi_model_dispatcher import get_model_for_user, get_api_key_for_user
import openai

app = Flask(__name__)

@app.route("/ai/chat", methods=["POST"])
def ai_chat():
    data = request.json
    user_id = data.get("user_id")
    message = data.get("message")
    
    model = get_model_for_user(user_id)
    api_key = get_api_key_for_user(user_id)
    
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": message}]
    )
    
    return jsonify({
        "status": "ok",
        "model": model,
        "response": response.choices[0].message.content
    })
```

---

## 🎯 最佳实践

### 1. **模型选择**
- Free 用户：使用 `gpt-4o-mini`（快速 + 低成本）
- Pro 用户：使用 `gpt-4-turbo`（高质量）
- Superintendent Admin：使用最先进模型（顶级性能）

### 2. **配置更新**
- 在 `ai_rules` 表中更新配置
- 无需重启系统即可生效
- 使用 `updated_by` 字段记录修改人

### 3. **监控与优化**
- 定期检查各模型的使用量
- 监控 token 消耗和成本
- 根据用户反馈调整模型选择

---

## 🛠️ 故障排查

### 问题 1: 所有用户都使用默认模型

**原因**: `ai_rules` 表不存在或为空

**解决**:
```bash
# 执行 SQL schema 创建表
psql $DATABASE_URL < sql/ai_rules_schema.sql
```

### 问题 2: Superintendent Admin 没有使用 LYNKER_MASTER_KEY

**原因**: Secret 未设置或用户 role 不正确

**解决**:
1. 检查 Replit Secrets 中是否有 `LYNKER_MASTER_KEY`
2. 检查用户表中 role 字段是否为 `"Superintendent Admin"`

### 问题 3: 配置更新后未生效

**原因**: 可能需要重新加载配置

**解决**:
- 重启 Flask API workflow
- 或调用 `load_ai_rules()` 强制刷新

---

## 📈 性能优化

### 1. **缓存规则**
```python
from functools import lru_cache

@lru_cache(maxsize=1)
def load_ai_rules_cached():
    return load_ai_rules()
```

### 2. **批量查询**
```python
def get_models_for_users(user_ids: list):
    """批量获取用户模型"""
    users = client.table("users").select("id, role, ai_provider").in_("id", user_ids).execute()
    rules = load_ai_rules()
    
    result = {}
    for user in users.data:
        # 应用规则...
        result[user["id"]] = model
    
    return result
```

---

## 🎉 总结

`multi_model_dispatcher.py` 提供了：

✅ **自动化模型选择** - 根据用户等级智能匹配  
✅ **动态配置管理** - 无需重启即可更新规则  
✅ **安全 Key 分发** - 权限隔离和成本控制  
✅ **降级保护** - 确保系统稳定性  
✅ **易于集成** - 简单的函数调用即可使用  

---

**文档版本**: 1.0  
**最后更新**: 2025-10-23  
**维护者**: LynkerAI Team
