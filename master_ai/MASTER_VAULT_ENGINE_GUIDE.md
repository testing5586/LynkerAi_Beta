# 🔐 Master Vault Engine 使用指南

## 概述

Master Vault Engine v2.0 是 LynkerAI 的核心安全模块，用于加密存储和管理 Master AI 的学习成果和核心知识。

## 核心功能

✅ **AES256 加密**：使用 Fernet 加密算法保护敏感知识  
✅ **权限控制**：只有 Superintendent Admin 可以解密查看内容  
✅ **PostgreSQL 存储**：直接写入数据库，确保数据持久化  
✅ **完整审计**：记录创建者、时间、访问级别等元数据  

## 快速开始

### 1. 环境配置

确保以下密钥已在 Replit Secrets 中设置：

```bash
MASTER_VAULT_KEY      # 加密主密钥（32位以上安全字符串）
DATABASE_URL          # PostgreSQL 连接 URL
SUPABASE_URL          # Supabase 项目 URL（可选）
SUPABASE_KEY          # Supabase API Key（可选）
```

### 2. 基本用法

```python
from master_vault_engine import insert_vault, read_vault, list_vault_entries

# 存入加密知识
insert_vault(
    title="AI命理学习记录#001",
    content="Master AI 在学习刻分算法时发现：23:10~23:12为关键命刻区间。",
    created_by="Master AI"
)

# Superintendent Admin 读取
decrypted = read_vault("AI命理学习记录#001", role="Superintendent Admin")

# 列出所有条目
list_vault_entries()
```

### 3. 运行测试

```bash
python master_vault_engine.py
```

预期输出：
```
🚀 LynkerAI Master Vault Engine v2.0
✅ 已写入 Vault：AI命理学习记录#001 (Master AI)
🔓 解密成功：AI命理学习记录#001
📝 内容：Master AI 在学习刻分算法时发现...
```

## API 文档

### `insert_vault(title, content, created_by, access_level)`

加密并存储知识到 Vault。

**参数：**
- `title` (str): 知识标题
- `content` (str): 明文内容（将被自动加密）
- `created_by` (str): 创建者，默认 "Master AI"
- `access_level` (str): 访问级别，默认 "restricted"

**返回：** UUID（Vault 记录 ID）

### `read_vault(title, role)`

根据标题读取并解密 Vault 内容。

**参数：**
- `title` (str): 知识标题
- `role` (str): 用户角色（必须是 "Superintendent Admin" 才能解密）

**返回：** 解密后的内容字符串，或 None（无权限/不存在）

**异常：** `PermissionError` - 无权限访问

### `list_vault_entries(role)`

列出所有 Vault 条目（仅元数据，不解密内容）。

**返回：** 条目列表（tuple）

## 数据库架构

```sql
CREATE TABLE master_vault (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT,
  encrypted_content TEXT,        -- AES256 加密内容
  access_level TEXT DEFAULT 'restricted',
  created_by TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 安全机制

### 加密算法
- **算法**：Fernet (AES-128-CBC + HMAC)
- **密钥派生**：SHA-256(MASTER_VAULT_KEY)
- **编码**：Base64 URL-safe

### 权限模型
| 角色 | 权限 |
|------|------|
| Superintendent Admin | 🔓 完全访问（加密/解密） |
| Master AI | 📝 仅写入（加密） |
| User/Guest | 🚫 无访问权限 |

### 审计追踪
每条 Vault 记录包含：
- 创建者身份
- 创建时间戳
- 访问级别标记
- 唯一 UUID 标识

## 集成示例

### 与 Master AI 集成

```python
# Master AI 自动记录学习成果
def record_learning(insight: str):
    from master_vault_engine import insert_vault
    import datetime
    
    title = f"学习记录_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    insert_vault(
        title=title,
        content=insight,
        created_by="Master AI",
        access_level="restricted"
    )
```

### 与 Flask API 集成

```python
from flask import Flask, jsonify, request
from master_vault_engine import insert_vault, read_vault

app = Flask(__name__)

@app.route("/api/vault/read", methods=["POST"])
def api_read_vault():
    data = request.json
    title = data.get("title")
    role = data.get("role")
    
    try:
        content = read_vault(title, role)
        return jsonify({"success": True, "content": content})
    except PermissionError as e:
        return jsonify({"success": False, "error": str(e)}), 403
```

## 常见问题

### Q: 忘记 MASTER_VAULT_KEY 怎么办？
A: 加密数据将永久无法恢复。务必安全保存此密钥！

### Q: 如何备份 Vault 数据？
A: 备份整个 PostgreSQL 数据库的 `master_vault` 表。

### Q: 可以修改已加密的内容吗？
A: 需要先用 Superintendent Admin 权限解密，修改后重新加密存入。

### Q: 支持批量导入吗？
A: 可以编写脚本循环调用 `insert_vault()`。

## 开发路线图

- [ ] 支持多级权限（Admin, Guru, User）
- [ ] 版本控制（记录修改历史）
- [ ] 自动备份到云端
- [ ] Web 管理界面
- [ ] 审计日志系统

## 相关文档

- [LynkerAI 核心架构](../docs/lynker_ai_core_index_v2.docx)
- [TMS 系统文档](README_TMS_v1.md)
- [Multi-Provider 管理器](README_PROVIDER_MANAGER.md)

---

**创建时间：** 2025-10-23  
**版本：** v2.0  
**维护者：** LynkerAI Master AI
