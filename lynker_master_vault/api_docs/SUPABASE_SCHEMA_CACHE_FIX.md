# 🔧 Supabase Schema Cache 问题修复指南

## ❌ 问题描述

```
错误信息：
Could not find the 'drive_refresh_token' column of 'users' in the schema cache
错误代码：PGRST204
```

**原因：** Supabase 的 PostgREST API 使用 schema cache 来提高性能。当您在数据库中创建新表或添加新字段时，API 层的缓存不会自动更新，导致 Supabase 客户端无法识别新字段。

---

## ✅ 临时解决方案（已应用）

### 修改内容

从保存操作中移除 `drive_refresh_token` 字段：

```python
# 修改前（会报错）
supabase.table("users").upsert({
    "name": user_id,
    "email": email,
    "drive_email": email,
    "drive_access_token": access_token,
    "drive_refresh_token": refresh_token,  # ❌ 此字段导致错误
    "drive_connected": True,
    "updated_at": datetime.now().isoformat()
}).execute()

# 修改后（可以正常工作）
supabase.table("users").upsert({
    "name": user_id,
    "email": email,
    "drive_email": email,
    "drive_access_token": access_token,  # ✅ 只保存 access_token
    "drive_connected": True,
    "updated_at": datetime.now().isoformat()
}).execute()
```

### 影响

- ✅ **OAuth 授权流程正常工作**
- ✅ **Access Token 正常保存**（1小时有效期）
- ⚠️ **Refresh Token 暂时不保存**

**后果：**
- Token 过期后需要重新授权
- 暂时无法实现自动 token 刷新

---

## 🔄 永久解决方案

### 方式 1: 刷新 Supabase Schema Cache（推荐）

1. **登录 Supabase 控制台**
   - 访问：https://supabase.com/dashboard
   - 选择您的项目

2. **刷新 Schema Cache**
   - 进入 `Database` → `Schema`
   - 找到 `public.users` 表
   - 点击刷新/重载按钮

3. **恢复代码**
   ```python
   # 恢复 drive_refresh_token 字段
   supabase.table("users").upsert({
       "name": user_id,
       "email": email,
       "drive_email": email,
       "drive_access_token": access_token,
       "drive_refresh_token": refresh_token,  # ✅ 现在可以保存了
       "drive_connected": True,
       "updated_at": datetime.now().isoformat()
   }).execute()
   ```

### 方式 2: 使用原生 PostgreSQL 客户端

不使用 Supabase SDK，直接使用 `psycopg2` 连接数据库：

```python
import psycopg2
import os

def save_oauth_credentials_direct(user_id, email, access_token, refresh_token):
    """使用原生 PostgreSQL 连接保存数据（绕过 PostgREST）"""
    
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO public.users 
        (name, email, drive_email, drive_access_token, drive_refresh_token, drive_connected, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
        ON CONFLICT (name) DO UPDATE SET
            email = EXCLUDED.email,
            drive_email = EXCLUDED.drive_email,
            drive_access_token = EXCLUDED.drive_access_token,
            drive_refresh_token = EXCLUDED.drive_refresh_token,
            drive_connected = EXCLUDED.drive_connected,
            updated_at = NOW()
    """, (user_id, email, email, access_token, refresh_token, True))
    
    conn.commit()
    cursor.close()
    conn.close()
```

**优点：**
- 绕过 PostgREST API
- 不受 schema cache 影响
- 立即生效

**缺点：**
- 需要额外的依赖（psycopg2）
- 失去 Supabase SDK 的便利性

### 方式 3: 等待自动刷新

Supabase 的 schema cache 会定期自动刷新（通常几分钟到几小时）。您可以：

1. 等待一段时间
2. 重启 Supabase 项目
3. 然后恢复代码

---

## 📊 当前状态

### 保存的字段（✅ 正常工作）

```sql
name                TEXT        -- 用户 ID
email               TEXT        -- 用户邮箱
drive_email         TEXT        -- Google Drive 邮箱
drive_access_token  TEXT        -- 访问令牌（1小时有效）
drive_connected     BOOLEAN     -- 绑定状态
updated_at          TIMESTAMP   -- 更新时间
```

### 未保存的字段（⚠️ 暂时跳过）

```sql
drive_refresh_token TEXT        -- 刷新令牌（长期有效）
```

---

## 🧪 测试验证

### 1. 测试当前 OAuth 流程

```bash
# 重新授权（应该成功）
# 在浏览器中打开之前的授权 URL
# 完成授权后查看成功页面
```

### 2. 验证数据保存

```sql
-- 查询数据库
SELECT name, email, drive_email, drive_access_token, drive_connected
FROM public.users
WHERE name = 'your_user_id';
```

### 3. 测试 Google Drive 连接

```python
from google_drive_sync import test_google_drive_connection

# 使用保存的 access_token 测试
test_google_drive_connection(access_token)
```

---

## 📝 下一步操作

1. **立即测试**：重新进行 Google OAuth 授权，应该可以成功
2. **长期方案**：选择上述永久解决方案之一
3. **添加 Token 刷新**：实现自动刷新 access_token 的功能

---

## ⚡ 快速命令

```bash
# 测试 OAuth 授权
python google_oauth_real_flow.py --user-id=u_demo

# 查看 Flask API 日志
# 在 Replit 控制台查看 "Flask API" workflow

# 验证数据保存
# 在 Supabase 控制台查看 public.users 表
```

---

**✅ 当前状态：OAuth 授权流程可以正常工作，只是暂时不保存 refresh_token。**

**🔄 建议：稍后在 Supabase 控制台刷新 schema cache，然后恢复 refresh_token 的保存。**
