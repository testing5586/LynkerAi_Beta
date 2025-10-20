# 🔐 Google OAuth 授权测试指南

## ✅ 脚本已优化

**文件：** `google_oauth_real_flow.py`

**优化内容：**
1. ✅ 使用 Google OAuth v1 API：`https://www.googleapis.com/oauth2/v1/userinfo?alt=json`
2. ✅ 保存到 Supabase 时包含 `updated_at` 时间戳
3. ✅ 优化打印格式，更简洁友好
4. ✅ 自动测试 Google Drive 连接

---

## 🚀 运行测试

### 执行命令

```bash
python google_oauth_real_flow.py --user-id=u_demo
```

---

## 📝 预期执行流程

### Step 1: 读取配置

```
============================================================
🔐 Google OAuth 2.0 真实授权流程
============================================================

📋 Step 1: 读取 OAuth 配置...
✅ Client ID: 85639669324-260ej89u...
✅ Redirect URI: https://lynkerai.replit.app
```

### Step 2: 生成授权 URL

```
🔗 Step 2: 生成授权 URL...

============================================================
📌 请复制以下 URL 到浏览器打开并授权：
============================================================

https://accounts.google.com/o/oauth2/v2/auth?client_id=...

============================================================
完成后复制浏览器地址栏中的 code 参数，粘贴回控制台。
============================================================
```

### Step 3: 输入授权码

```
🔑 请输入授权码（code 参数的值）：[粘贴授权码]
```

### Step 4: 换取 Token

```
🔄 Step 3: 用授权码换取 access_token...
✅ Access Token: ya29.a0AeDC...
✅ Refresh Token: 1//0gXj7vK...
```

### Step 5: 获取用户信息

```
👤 Step 4: 获取用户信息...
✅ 用户邮箱：user@gmail.com
✅ 用户名称：Demo User
```

### Step 6: 保存到 Supabase

```
💾 Step 5: 保存到 Supabase.users...

============================================================
✅ 授权成功！
📧 邮箱：user@gmail.com
🔑 Token：ya29.a0AeD...
💾 已保存到 Supabase.users
============================================================
```

### Step 7: 测试连接

```
🧪 测试 Google Drive 连接...
✅ Google Drive 连接成功！用户：user@gmail.com
✅ Google Drive 连接测试成功！

📊 下一步操作：
   1. 生成子AI记忆：python child_ai_memory.py
   2. 记忆会自动同步到 Google Drive
```

---

## 📊 保存到 Supabase 的数据

### 更新的字段

```sql
UPDATE users SET
  drive_connected = TRUE,
  drive_access_token = 'ya29.a0AeDClZD...',
  drive_refresh_token = '1//0gXj7vKZq...',
  drive_email = 'user@gmail.com',
  updated_at = '2025-10-19T12:34:56.789012'
WHERE name = 'u_demo';
```

---

## 🔍 授权流程详解

### 1️⃣ 生成授权 URL

**端点：** `https://accounts.google.com/o/oauth2/v2/auth`

**参数：**
- `client_id`: 您的 OAuth 客户端 ID
- `redirect_uri`: 授权后重定向地址
- `response_type`: `code`（授权码模式）
- `scope`: `drive.file`, `userinfo.email`, `openid`
- `access_type`: `offline`（获取 refresh_token）
- `prompt`: `consent`（强制显示授权页面）

### 2️⃣ 用户授权

1. 打开授权 URL
2. 选择 Google 账号
3. 查看权限请求
4. 点击"允许"

### 3️⃣ 获取授权码

授权后，Google 会重定向到：
```
https://lynkerai.replit.app?code=4/0AeanS0ZP-xxx...
```

复制 `code` 参数的值（`4/0AeanS0ZP-xxx...`）

### 4️⃣ 换取 Access Token

**端点：** `https://oauth2.googleapis.com/token`

**POST 数据：**
```json
{
  "code": "4/0AeanS0ZP...",
  "client_id": "...",
  "client_secret": "...",
  "redirect_uri": "https://lynkerai.replit.app",
  "grant_type": "authorization_code"
}
```

**响应：**
```json
{
  "access_token": "ya29.a0AeDClZD...",
  "refresh_token": "1//0gXj7vKZq...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

### 5️⃣ 获取用户信息

**端点：** `https://www.googleapis.com/oauth2/v1/userinfo?alt=json`

**请求头：** `Authorization: Bearer {access_token}`

**响应：**
```json
{
  "email": "user@gmail.com",
  "name": "Demo User",
  "picture": "https://..."
}
```

---

## 🧪 测试场景

### 场景 1：首次授权（推荐）

```bash
python google_oauth_real_flow.py --user-id=u_demo
```

**预期结果：**
- ✅ 生成授权 URL
- ✅ 用户完成授权
- ✅ 获取 access_token 和 refresh_token
- ✅ 保存到 Supabase users 表
- ✅ drive_connected = TRUE

### 场景 2：不保存到 Supabase

```bash
python google_oauth_real_flow.py
```

**预期结果：**
- ✅ 生成授权 URL
- ✅ 获取 access_token
- ⚠️ 不保存到 Supabase（仅测试授权流程）

---

## ⚠️ 常见问题

### Q1: 授权码无效？

**错误信息：** `Token 交换失败：400`

**可能原因：**
1. 授权码已使用（每个 code 只能用一次）
2. 授权码已过期（10分钟有效期）
3. 复制时包含了额外的空格或字符

**解决方法：**
1. 重新运行脚本获取新的授权 URL
2. 重新授权获取新的 code
3. 确保复制时没有多余的空格

### Q2: 重定向到 404 页面？

**A:** 这是正常现象！
- `https://lynkerai.replit.app` 可能还没有对应的页面
- 只需复制浏览器地址栏的 URL，提取 `code` 参数即可

### Q3: Supabase 保存失败？

**错误信息：** `更新失败`

**可能原因：**
1. `users` 表缺少 `drive_*` 字段
2. `user_id` (name 字段) 不存在

**解决方法：**
```bash
# 运行自动修复脚本
python fix_supabase_users_schema.py
```

---

## 📈 授权成功后的操作

### 1️⃣ 验证绑定状态

```python
from supabase_init import init_supabase

supabase = init_supabase()
result = supabase.table('users').select('*').eq('name', 'u_demo').execute()

user = result.data[0]
print(f"绑定状态：{user['drive_connected']}")
print(f"邮箱：{user['drive_email']}")
```

### 2️⃣ 生成并同步子AI记忆

```bash
python child_ai_memory.py
```

**预期输出：**
```
✅ 记忆同步完成：新建 5 条，更新 3 条
☁️ 正在上传子AI记忆到 Google Drive ...
✅ 找到已存在的文件夹：LynkerAI_Memories
✅ 文件已上传到 Google Drive：lynker_ai_memories_u_demo_20251019.json
✅ Google Drive 同步成功！
```

### 3️⃣ 手动同步记忆

```python
from google_drive_sync import auto_sync_user_memories

result = auto_sync_user_memories("u_demo")
print(result)
```

---

## 🔄 Token 管理

### Access Token

- **有效期：** 1 小时
- **用途：** 访问 Google Drive API
- **刷新：** 使用 refresh_token 获取新的 access_token

### Refresh Token

- **有效期：** 长期有效（直到用户撤销授权）
- **用途：** 获取新的 access_token
- **存储：** Supabase users 表的 `drive_refresh_token` 字段

### 未来优化

- [ ] 实现自动 token 刷新机制
- [ ] 检测 token 过期并自动刷新
- [ ] 避免用户频繁重新授权

---

**🎉 准备就绪！现在可以运行脚本进行真实的 Google OAuth 授权了！**

```bash
python google_oauth_real_flow.py --user-id=u_demo
```
