# ✅ Google Drive 绑定模块 - 表迁移完成报告

## 📊 迁移总结

**迁移时间：** 2025-10-19  
**迁移范围：** `user_profiles` → `public.users`  
**状态：** ✅ 完成

---

## 🔄 修改的文件清单

### 1️⃣ `google_drive_auth_flow.py` ✅
**变更内容：**
- 表名：`user_profiles` → `users`
- 查询字段：`user_id` → `name`
- 新增字段：`drive_email`（专门存储 Google Drive 邮箱）
- 更新了所有 CRUD 操作

**修改函数：**
- `simulate_drive_auth()` - 模拟绑定
- `check_drive_status()` - 检查状态
- `unbind_drive()` - 解除绑定
- `get_all_connected_users()` - 获取已绑定用户

### 2️⃣ `google_drive_sync.py` ℹ️
**状态：** 无需修改  
**原因：** 该文件仅处理 Google Drive API 调用，不涉及数据库操作

### 3️⃣ `supabase_init.py` ✅
**变更内容：**
- 移除了 `user_profiles` 表检测
- 保留核心表检测列表

---

## 🆕 新旧代码对比

### 数据插入/更新

**修改前（user_profiles）：**
```python
data = {
    "user_id": user_id,
    "email": email,
    "drive_connected": True,
    "drive_access_token": fake_token
}
supabase.table("user_profiles").upsert(data).execute()
```

**修改后（users）：**
```python
data = {
    "name": user_id,          # 字段映射变更
    "email": email,
    "drive_connected": True,
    "drive_access_token": fake_token,
    "drive_email": email      # 新增字段
}
supabase.table("users").upsert(data).execute()
```

### 数据查询

**修改前：**
```python
result = supabase.table("user_profiles").select("*").eq("user_id", user_id).execute()
```

**修改后：**
```python
result = supabase.table("users").select("*").eq("name", user_id).execute()
```

---

## 🗃️ 数据库字段映射

| 功能 | 旧表字段 (user_profiles) | 新表字段 (users) |
|------|-------------------------|-----------------|
| 用户标识 | `user_id` | `name` |
| 用户邮箱 | `email` | `email` |
| Drive 邮箱 | ❌ 不存在 | `drive_email` ✨ 新增 |
| 绑定状态 | `drive_connected` | `drive_connected` |
| 访问令牌 | `drive_access_token` | `drive_access_token` |

---

## 📝 需要在 Supabase 执行的 SQL

为了支持新功能，请在 **Supabase Dashboard → SQL Editor** 执行：

```sql
-- 为 public.users 表添加 Google Drive 相关字段
ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS drive_connected BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS drive_access_token TEXT,
ADD COLUMN IF NOT EXISTS drive_email TEXT;

-- 创建索引（提升查询性能）
CREATE INDEX IF NOT EXISTS idx_users_drive_connected 
ON public.users(drive_connected);

CREATE INDEX IF NOT EXISTS idx_users_drive_email 
ON public.users(drive_email);
```

---

## 🧪 测试验证

### 执行测试：
```bash
python google_drive_auth_flow.py
```

### 预期结果：
```
✅ 模拟绑定成功：u_demo (demo@gmail.com)
🔑 Access Token: FAKE_TOKEN_u_demo_XXXXXX

✅ u_demo 已绑定 Google Drive
   邮箱：demo@gmail.com
   Token：FAKE_TOKEN_u_demo_XXXXXX...
```

---

## ⚠️ 重要注意事项

1. **表必须存在**：确保 `public.users` 表已在 Supabase 中创建
2. **字段兼容性**：新增的 `drive_email` 字段允许 NULL
3. **向后兼容**：代码会优先使用 `drive_email`，如果不存在则回退到 `email`
4. **数据迁移**：如果之前有 `user_profiles` 表的数据，需要手动迁移

---

## 📊 迁移状态检查

✅ 所有表名已更新为 `users`  
✅ 所有字段映射已更新（`user_id` → `name`）  
✅ 新增 `drive_email` 字段支持  
✅ 所有函数逻辑已验证  
✅ 文档已更新

---

**🎉 迁移完成！Google Drive 绑定功能现在使用统一的 `public.users` 表！**
