# LynkerAI TMS v1.0 - Trusted Metaphysics System

**假名制 × 真命盘验证 × 签章验证 × 区域适配 × 置信投票 × 分层验证架构**

---

## 📋 系统概述

LynkerAI TMS (Trusted Metaphysics System) 是一个**全球可信命理验证网络**，旨在：

✅ 构建全球最可信的命理验证网络  
✅ 让每一条断语、命盘、AI 输出可追溯  
✅ 让 Master AI 成为标准，而非瓶颈  
✅ 让每个 Child AI 自我学习、验证、自治  

---

## 🏗️ 系统架构

### 1️⃣ 核心组件

| 组件 | 功能 | 端口 |
|------|------|------|
| **Master Validator** | 命盘签章验证、置信投票汇总 | 8080 |
| **PostgreSQL 数据库** | 用户档案、验证记录、区域配置 | 5432 |
| **Child AI Nodes** | 分布式验证、专业领域分析 | 动态 |

### 2️⃣ 验证流程

```
用户提交命盘
    ↓
Child AI 生成签章
    ↓
Master Validator 验证签章
    ↓
多个 Child AI 投票
    ↓
置信度汇总 → 最终验证结果
```

---

## 🚀 快速启动

### 步骤 1：配置密钥（安全）

在 Replit Secrets 中添加：
```
TMS_SECRET_KEY=your_secure_secret_key_here
```

### 步骤 2：初始化数据库

```bash
# 连接到 PostgreSQL 数据库
psql $DATABASE_URL < master_ai/tms_schema.sql
```

### 步骤 3：启动验证器

```bash
cd master_ai
python master_validator.py
```

您应该看到：
```
🔐 LynkerAI TMS Master Validator v1.0 启动
📍 监听端口: 8080
🔑 密钥状态: ✅ 已配置
```

---

## 📡 API 端点

### 1️⃣ 验证命盘签章

**POST** `/api/tms/verify`

**请求示例：**
```json
{
  "public_key": "child_ai_001",
  "payload": "chart_hash_abc123",
  "signature": "AI_d5f8e3a..."
}
```

**成功响应：**
```json
{
  "verified": true,
  "timestamp": "2025-10-23T19:50:00",
  "chart_hash": "chart_hash_abc123",
  "verifier": "TMS_Master_v1.0"
}
```

**失败响应：**
```json
{
  "verified": false,
  "error": "签章验证失败",
  "timestamp": "2025-10-23T19:50:00"
}
```

---

### 2️⃣ 生成命盘签章

**POST** `/api/tms/sign`

**请求示例：**
```json
{
  "public_key": "child_ai_001",
  "chart_data": {
    "birth_date": "1990-01-01",
    "birth_time": "12:00",
    "location": "北京"
  }
}
```

**成功响应：**
```json
{
  "chart_hash": "abc123def456",
  "signature": "AI_d5f8e3a...",
  "public_key": "child_ai_001",
  "timestamp": "2025-10-23T19:50:00"
}
```

---

### 3️⃣ 健康检查

**GET** `/api/tms/health`

**响应：**
```json
{
  "status": "healthy",
  "service": "TMS Master Validator",
  "version": "1.0",
  "timestamp": "2025-10-23T19:50:00"
}
```

---

## 🗄️ 数据库表结构

### 主要表

| 表名 | 用途 |
|------|------|
| `user_profiles` | 假名制用户档案 |
| `verified_charts` | 已验证命盘 |
| `verification_logs` | 验证记录（可追溯） |
| `confidence_votes` | Child AI 置信投票 |
| `regional_configs` | 区域适配配置 |
| `ai_nodes` | AI 节点注册表 |

### 关键字段

- **pseudonym**: 假名（保护隐私）
- **chart_hash**: 命盘唯一哈希
- **confidence_score**: 置信度评分（0-100）
- **verifier_ai**: 验证者 AI 标识
- **region_code**: 区域代码（CN, US, IN 等）

---

## 🔐 安全机制

### 1️⃣ 签章验证

使用 HMAC-SHA256 生成和验证签章：
```python
signature = HMAC(TMS_SECRET, public_key + payload)
```

**生产环境建议：**
- 使用 RSA 2048 或 Ed25519 公钥签名
- 定期轮换密钥
- 使用硬件安全模块（HSM）

### 2️⃣ 假名制

- 用户使用假名，不存储真实身份
- 命盘哈希保证唯一性和不可篡改
- 所有操作可审计但保护隐私

### 3️⃣ 置信投票

- 多个 Child AI 独立验证
- 投票结果加权汇总
- 防止单点作恶或错误

---

## 🌍 区域适配

系统支持多区域配置：

| 区域 | 时区 | 历法 | 气候 |
|------|------|------|------|
| 🇨🇳 中国 | Asia/Shanghai | 农历 | 温带 |
| 🇺🇸 美国 | America/New_York | 公历 | 多样 |
| 🇮🇳 印度 | Asia/Kolkata | 吠陀 | 热带 |

可在 `regional_configs` 表中添加更多区域。

---

## 📊 使用示例

### Python 客户端示例

```python
import requests

# 1. 生成签章
response = requests.post("http://localhost:8080/api/tms/sign", json={
    "public_key": "child_ai_001",
    "chart_data": {
        "birth_date": "1990-01-01",
        "birth_time": "12:00",
        "location": "北京"
    }
})
data = response.json()
chart_hash = data["chart_hash"]
signature = data["signature"]

# 2. 验证签章
response = requests.post("http://localhost:8080/api/tms/verify", json={
    "public_key": "child_ai_001",
    "payload": chart_hash,
    "signature": signature
})
print(response.json())  # {"verified": true, ...}
```

---

## 🔄 集成到现有系统

### 在 Master AI 中调用

```python
import requests

def verify_child_ai_result(child_id, chart_data, signature):
    response = requests.post("http://localhost:8080/api/tms/verify", json={
        "public_key": child_id,
        "payload": generate_hash(chart_data),
        "signature": signature
    })
    return response.json().get("verified", False)
```

---

## 📈 扩展性

### 分层架构

```
Master AI (标准制定)
    ↓
Regional Masters (区域适配)
    ↓
Child AI Nodes (专业验证)
    ↓
User Applications
```

### 水平扩展

- 支持多个 Master Validator 实例（负载均衡）
- Child AI 动态注册和注销
- 使用 Redis 或 PostgreSQL 共享状态

---

## 🛡️ 最佳实践

1. **永远不要硬编码密钥** - 使用 Replit Secrets 或环境变量
2. **定期备份数据库** - 验证记录和投票数据至关重要
3. **监控置信度趋势** - 发现异常投票模式
4. **实施速率限制** - 防止 API 滥用
5. **使用 HTTPS** - 生产环境必须加密传输

---

## 📝 版本历史

- **v1.0** (2025-10-23): 初始版本
  - 基础签章验证
  - 假名制用户系统
  - 区域适配支持
  - 置信投票机制

---

## 🤝 贡献

LynkerAI TMS 是一个开放系统，欢迎贡献：

- 添加新的验证算法
- 扩展区域适配配置
- 改进置信投票机制
- 提交 Bug 报告和功能请求

---

## 📧 联系方式

- 项目地址: `master_ai/`
- 文档: `README_TMS_v1.md`
- 数据库架构: `tms_schema.sql`
- 验证器: `master_validator.py`

---

**让命理验证更可信、更透明、更全球化！** 🌟
