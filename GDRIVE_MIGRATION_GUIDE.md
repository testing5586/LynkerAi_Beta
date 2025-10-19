# 🔄 Google Drive 绑定模块 - 表迁移指南

## 📋 迁移概述

**迁移原因：** 从 `user_profiles` 表迁移到系统统一的 `public.users` 表

**修改范围：**
- ✅ `google_drive_auth_flow.py` - 已更新
- ℹ️ `google_drive_sync.py` - 无需修改（不涉及数据库操作）

---

## 🔄 字段映射变更

### 旧表：user_profiles
```
user_id → 用户标识
email → 用户邮箱
drive_connected → 绑定状态
drive_access_token → 访问令牌
```

### 新表：public.users
```
name → 用户标识（对应旧 user_id）
email → 用户邮箱
drive_email → Google Drive 邮箱（新增）
drive_connected → 绑定状态
drive_access_token → 访问令牌
```

---

## 📊 代码变更对比

### 1️⃣ simulate_drive_auth() 函数

**修改前：**
```python
data = {
    "user_id": user_id,
    "email": email,
    "drive_connected": True,
    "drive_access_token": fake_token,
    "drive_connected_at": datetime.now().isoformat()
}
result = supabase.table("user_profiles").upsert(data).execute()
```

**修改后：**
```python
data = {
    "name": user_id,  # users 表使用 name 字段
    "email": email,
    "drive_connected": True,
    "drive_access_token": fake_token,
    "drive_email": email  # 专门存储 Google Drive 邮箱
}
result = supabase.table("users").upsert(data).execute()
```

---

### 2️⃣ check_drive_status() 函数

**修改前：**
```python
result = supabase.table("user_profiles").select("*").eq("user_id", user_id).execute()
print(f"   邮箱：{profile.get('email')}")
```

**修改后：**
```python
result = supabase.table("users").select("*").eq("name", user_id).execute()
print(f"   邮箱：{profile.get('drive_email') or profile.get('email')}")
```

---

### 3️⃣ unbind_drive() 函数

**修改前：**
```python
data = {
    "user_id": user_id,
    "drive_connected": False,
    "drive_access_token": None,
    "drive_refresh_token": None
}
result = supabase.table("user_profiles").upsert(data).execute()
```

**修改后：**
```python
data = {
    "name": user_id,  # 使用 name 字段
    "drive_connected": False,
    "drive_access_token": None,
    "drive_email": None
}
result = supabase.table("users").upsert(data).execute()
```

---

### 4️⃣ get_all_connected_users() 函数

**修改前：**
```python
result = supabase.table("user_profiles").select("*").eq("drive_connected", True).execute()
for user in result.data:
    print(f"  - {user['user_id']} ({user['email']})")
```

**修改后：**
```python
result = supabase.table("users").select("*").eq("drive_connected", True).execute()
for user in result.data:
    user_name = user.get('name', 'Unknown')
    user_email = user.get('drive_email') or user.get('email', 'N/A')
    print(f"  - {user_name} ({user_email})")
```

---

## 🗃️ 数据库表结构要求

在 **Supabase Dashboard → SQL Editor** 执行：

```sql
-- 为 public.users 表添加 Google Drive 相关字段
ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS drive_connected BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS drive_access_token TEXT,
ADD COLUMN IF NOT EXISTS drive_email TEXT;

-- 创建索引（可选，提升查询性能）
CREATE INDEX IF NOT EXISTS idx_users_drive_connected 
ON public.users(drive_connected);

CREATE INDEX IF NOT EXISTS idx_users_drive_email 
ON public.users(drive_email);
```

---

## 🧪 测试验证

### 执行测试脚本：
```bash
python google_drive_auth_flow.py
```

### 预期输出：
```
🧪 测试 Google Drive 绑定流程模拟器

============================================================
1️⃣ 模拟用户绑定 Google Drive
============================================================
✅ 模拟绑定成功：u_demo (demo@gmail.com)
🔑 Access Token: FAKE_TOKEN_u_demo_1739928341

============================================================
2️⃣ 检查绑定状态
============================================================
✅ u_demo 已绑定 Google Drive
   邮箱：demo@gmail.com
   Token：FAKE_TOKEN_u_demo_1739928341...

============================================================
3️⃣ 获取所有已绑定用户
============================================================
📊 已绑定 Google Drive 的用户数量：1

  - u_demo (demo@gmail.com)

✅ 测试完成！
```

---

## ⚠️ 重要提示

1. **表依赖性**：确保 `public.users` 表已经存在
2. **字段兼容**：新增的 `drive_email` 字段用于区分系统邮箱和 Google Drive 邮箱
3. **数据迁移**：如果之前有 `user_profiles` 表的数据，需要手动迁移到 `users` 表

---

## 📁 修改的文件清单

- ✅ `google_drive_auth_flow.py` - 已更新所有数据库操作
- ℹ️ `google_drive_sync.py` - 无需修改（不涉及数据库）
- 📝 `GDRIVE_MIGRATION_GUIDE.md` - 本文档

---

**🎉 迁移完成！现在 Google Drive 绑定功能使用统一的 users 表！**
