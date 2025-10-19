# 🧪 Google Drive 绑定模拟机制 - 设置指南

## 📋 概述

这是一个**模拟的** Google Drive 绑定流程，不需要真实的 Google API 连接。  
目标是建立绑定机制框架，为后续使用样板 Gmail 账号测试做准备。

---

## 🛠️ 前置准备

### 1️⃣ 创建 Supabase 表

在 Supabase Dashboard 的 SQL Editor 中执行以下 SQL：

```sql
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE,
    email TEXT,
    drive_connected BOOLEAN DEFAULT FALSE,
    drive_access_token TEXT,
    drive_refresh_token TEXT,
    drive_connected_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON public.user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON public.user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_user_profiles_drive_connected ON public.user_profiles(drive_connected);
```

或者直接执行项目中的 `create_user_profiles_table.sql` 文件。

---

## 🧪 使用模拟绑定功能

### 1️⃣ 模拟用户绑定

```bash
python google_drive_auth_flow.py
```

**预期输出：**
```
🧪 测试 Google Drive 绑定流程模拟器

============================================================
1️⃣ 模拟用户绑定 Google Drive
============================================================
✅ 模拟绑定成功：u_demo (demo@gmail.com)
🔑 Access Token: FAKE_TOKEN_u_demo_1739927341

============================================================
2️⃣ 检查绑定状态
============================================================
✅ u_demo 已绑定 Google Drive
   邮箱：demo@gmail.com
   绑定时间：2025-01-19T10:22:21

============================================================
3️⃣ 获取所有已绑定用户
============================================================
📊 已绑定 Google Drive 的用户数量：1

  - u_demo (demo@gmail.com)

✅ 测试完成！
```

---

## 📚 API 函数说明

### `simulate_drive_auth(user_id, email)`

**模拟 Google Drive 绑定**

```python
from google_drive_auth_flow import simulate_drive_auth

result = simulate_drive_auth("u_test1", "test1@gmail.com")
# 返回：{"success": True, "user_id": "u_test1", "email": "test1@gmail.com", "token": "FAKE_TOKEN_..."}
```

### `check_drive_status(user_id)`

**检查用户绑定状态**

```python
from google_drive_auth_flow import check_drive_status

profile = check_drive_status("u_demo")
# 返回用户配置字典，包含 drive_connected, email 等信息
```

### `unbind_drive(user_id)`

**解除 Google Drive 绑定**

```python
from google_drive_auth_flow import unbind_drive

result = unbind_drive("u_demo")
# 返回：{"success": True}
```

### `get_all_connected_users()`

**获取所有已绑定用户**

```python
from google_drive_auth_flow import get_all_connected_users

users = get_all_connected_users()
# 返回已绑定用户列表
```

---

## 🔄 工作流程

```
用户请求绑定 Google Drive
         ↓
调用 simulate_drive_auth(user_id, email)
         ↓
生成 FAKE_TOKEN (格式：FAKE_TOKEN_{user_id}_{timestamp})
         ↓
存入 Supabase user_profiles 表
         ↓
设置 drive_connected = True
         ↓
返回绑定成功
```

---

## 📊 数据库表结构

### `user_profiles` 表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BIGSERIAL | 主键 |
| user_id | TEXT | 用户ID（唯一） |
| email | TEXT | 用户邮箱 |
| drive_connected | BOOLEAN | 是否已绑定 Google Drive |
| drive_access_token | TEXT | 访问令牌（模拟） |
| drive_refresh_token | TEXT | 刷新令牌（预留） |
| drive_connected_at | TIMESTAMP | 绑定时间 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

## 🧪 测试场景

### 场景1：模拟多个用户绑定

```python
from google_drive_auth_flow import simulate_drive_auth

# 绑定多个测试用户
simulate_drive_auth("u_test1", "test1@gmail.com")
simulate_drive_auth("u_test2", "test2@gmail.com")
simulate_drive_auth("u_test3", "test3@gmail.com")
```

### 场景2：检查所有绑定状态

```python
from google_drive_auth_flow import get_all_connected_users

users = get_all_connected_users()
print(f"已绑定用户数：{len(users)}")
```

### 场景3：解除绑定

```python
from google_drive_auth_flow import unbind_drive, check_drive_status

# 解除绑定
unbind_drive("u_test1")

# 验证状态
check_drive_status("u_test1")  # 应显示未绑定
```

---

## 🎯 后续真实集成步骤

当准备使用真实 Google 账号时：

1. **替换 `simulate_drive_auth`**：
   - 改为真实的 Google OAuth 2.0 流程
   - 使用真实的 `access_token` 和 `refresh_token`

2. **更新 `google_drive_sync.py`**：
   - 从 `user_profiles` 表读取真实的 `access_token`
   - 调用真实的 Google Drive API

3. **前端集成**：
   - 使用 `GoogleDriveSyncButton.jsx` 完成真实授权
   - 将真实 token 传递给后端存储

---

## ⚠️ 注意事项

1. **这是模拟环境**：生成的 token 格式为 `FAKE_TOKEN_*`，不能用于真实 API 调用
2. **数据持久化**：所有绑定状态存储在 Supabase `user_profiles` 表中
3. **测试友好**：可以随时绑定/解绑，无需真实 Google 账号

---

## 📁 相关文件

```
LynkerAI/
├── google_drive_auth_flow.py          # 模拟绑定流程
├── google_drive_sync.py                # 文件上传模块（使用真实 token）
├── components/GoogleDriveSyncButton.jsx # 前端授权按钮
├── create_user_profiles_table.sql      # 建表 SQL
├── supabase_tables_schema.sql          # 完整 schema
└── GOOGLE_DRIVE_MOCK_SETUP.md          # 本文档
```

---

**🎉 模拟机制已就绪！可以开始测试绑定流程了！**
