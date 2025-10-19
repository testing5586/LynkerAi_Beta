# 📋 fix_supabase_users_schema.py - 使用指南

## 🎯 功能说明

这是一个**自动修复工具**，用于检测和修复 Supabase `public.users` 表的字段缺失问题。

---

## 🚀 使用方法

### 方式 1：直接运行（推荐）

```bash
python fix_supabase_users_schema.py
```

### 方式 2：作为模块导入

```python
from fix_supabase_users_schema import auto_fix_schema

# 自动检测并修复
success = auto_fix_schema()
```

---

## 📊 运行示例

### ✅ 正常情况（表结构完整）

```
============================================================
Supabase users 表结构自动修复工具
============================================================

✅ psycopg2 已安装

🔍 正在检测 Supabase users 表...
✅ 已找到表：users
✅ 表结构完整，所有字段都已存在！

🎉 表结构修复完成！
```

### ⚠️ 需要修复的情况

```
============================================================
Supabase users 表结构自动修复工具
============================================================

🔍 正在检测 Supabase users 表...
✅ 已找到表：users
⚠️ 发现缺失字段：drive_connected, drive_access_token, drive_email

⚙️ 修复中：添加缺失字段 drive_connected, drive_access_token, drive_email
✅ 修复完成并刷新缓存！

🎉 表结构修复完成！
```

---

## 🔍 检测的字段

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `drive_connected` | BOOLEAN | FALSE | Google Drive 是否已绑定 |
| `drive_access_token` | TEXT | NULL | Google OAuth 访问令牌 |
| `drive_email` | TEXT | NULL | Google Drive 邮箱 |

---

## 🛠️ 自动修复流程

```
启动脚本
    ↓
连接 Supabase
    ↓
检测 users 表字段
    ↓
    ├─ 完整 → 退出（无需修复）
    └─ 缺失 → 执行 SQL
            ↓
        ALTER TABLE public.users
        ADD COLUMN IF NOT EXISTS drive_connected BOOLEAN DEFAULT FALSE,
        ADD COLUMN IF NOT EXISTS drive_access_token TEXT,
        ADD COLUMN IF NOT EXISTS drive_email TEXT;
            ↓
        刷新 PostgREST 缓存
            ↓
        修复完成
```

---

## ⚙️ 依赖要求

### 必需依赖：
- ✅ `supabase` - Supabase Python SDK
- ✅ `DATABASE_URL` 环境变量（用于直接数据库连接）

### 可选依赖：
- 💡 `psycopg2-binary` - 用于执行 DDL 语句（推荐安装）

如果没有 `psycopg2-binary`，脚本会显示需要手动执行的 SQL。

---

## 📝 手动安装 psycopg2（可选）

```bash
uv add psycopg2-binary
```

或者使用 pip：

```bash
pip install psycopg2-binary
```

---

## 🧪 API 函数

### `check_users_table_schema()`
检测 users 表字段是否完整

**返回：**
- `[]` - 所有字段都存在
- `['drive_email', ...]` - 缺失的字段列表
- `None` - 检测失败

### `fix_users_table_schema(missing_fields)`
修复缺失的字段

**参数：**
- `missing_fields` - 缺失字段列表

**返回：**
```python
{
    "success": True/False,
    "message": "操作结果",
    "sql": "SQL 语句（如果失败）"
}
```

### `auto_fix_schema()`
自动检测并修复（推荐使用）

**返回：**
- `True` - 修复成功或无需修复
- `False` - 修复失败

---

## ⚠️ 注意事项

1. **自动执行**：脚本会自动执行 SQL，无需确认
2. **幂等性**：多次运行不会重复添加字段（使用 `IF NOT EXISTS`）
3. **安全性**：只添加字段，不会删除或修改现有数据
4. **缓存刷新**：自动发送 `NOTIFY pgrst, 'reload schema'` 刷新 PostgREST

---

## 🔗 相关文件

- `google_drive_auth_flow.py` - Google Drive 绑定流程
- `google_drive_sync.py` - Google Drive 文件上传
- `SQL_FOR_USERS_TABLE.sql` - 手动执行的 SQL 脚本（备用）

---

**💡 提示：在运行 Google Drive 绑定功能前，建议先执行此脚本确保表结构完整！**
