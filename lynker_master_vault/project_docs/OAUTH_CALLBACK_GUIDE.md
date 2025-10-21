# 🔐 Google OAuth 回调服务使用指南

## ✅ 已完成集成

**Flask API 已集成 Google OAuth 回调功能！**

---

## 🚀 服务状态

- **服务地址：** https://f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de-00-3h1iq9ru0v8kp.sisko.replit.dev/
- **监听端口：** 5000
- **状态：** ✅ 运行中

---

## 📍 可用端点

### OAuth 回调端点

支持以下路由（都指向同一个处理函数）：

```
GET /
GET /callback
GET /oauth2callback
```

**功能：**
1. 接收 Google OAuth 回调
2. 用授权码换取 access_token
3. 获取用户信息（邮箱）
4. 保存到 Supabase users 表
5. 显示成功页面

### API 端点

```
POST /login_refresh  - 用户登入时触发匹配刷新
GET  /health         - 健康检查
```

---

## 🎯 OAuth 授权完整流程

### Step 1: 生成授权 URL

使用 `google_oauth_real_flow.py` 脚本生成授权 URL：

```bash
python google_oauth_real_flow.py --user-id=u_demo
```

**输出示例：**
```
============================================================
📌 请复制以下 URL 到浏览器打开并授权：
============================================================

https://accounts.google.com/o/oauth2/v2/auth?
client_id=85639669324-260ej89uej6g4khcb2fj306vk5vgfl28.apps.googleusercontent.com&
redirect_uri=https%3A%2F%2Ff7ebbceb-eb1c-41fc-9cf7-dbfc578e05de-00-3h1iq9ru0v8kp.sisko.replit.dev%2F&
response_type=code&
scope=...&
access_type=offline&
prompt=consent

============================================================
完成后复制浏览器地址栏中的 code 参数，粘贴回控制台。
============================================================
```

### Step 2: 用户授权

1. 在浏览器中打开授权 URL
2. 选择 Google 账号
3. 点击"允许"授权访问 Google Drive
4. 授权后自动重定向到回调地址

### Step 3: 自动处理回调

**重定向示例：**
```
https://f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de-00-3h1iq9ru0v8kp.sisko.replit.dev/?code=4/0AVGzR1D-xxx...
```

Flask API 会自动：
1. 提取 `code` 参数
2. 用 code 换取 access_token
3. 调用 `https://www.googleapis.com/oauth2/v1/userinfo?alt=json` 获取邮箱
4. 保存到 Supabase users 表

### Step 4: 显示成功页面

用户会看到一个漂亮的成功页面：

```
✅ Google Drive 绑定成功！

📧 用户邮箱：user@gmail.com
👤 用户名称：Demo User
🔑 Access Token：ya29.a0AeD...
💾 存储状态：已保存到 Supabase.users 表

🎉 您现在可以关闭此页面，返回应用继续操作。
```

---

## 💾 数据保存到 Supabase

### 保存的字段

```sql
UPDATE users SET
  name = 'user',                 -- 从邮箱提取的用户名
  email = 'user@gmail.com',      -- 完整邮箱地址
  drive_email = 'user@gmail.com', -- Google Drive 绑定邮箱
  drive_access_token = 'ya29.a0AeDClZD...', -- 访问令牌
  drive_refresh_token = '1//0gXj7vKZq...', -- 刷新令牌
  drive_connected = TRUE,         -- 绑定状态
  updated_at = '2025-10-21T10:00:00.123456' -- 更新时间
WHERE name = 'user';
```

---

## 🧪 测试场景

### 场景 1：访问主页（无 code 参数）

```bash
curl https://f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de-00-3h1iq9ru0v8kp.sisko.replit.dev/
```

**响应：**
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <title>LynkerAI API</title>
</head>
<body>
    <div class="info">
        <h2>🔐 LynkerAI API</h2>
        <p>此服务用于处理 Google OAuth 回调。</p>
        <p>如需授权，请从应用开始 OAuth 流程。</p>
    </div>
</body>
</html>
```

### 场景 2：OAuth 回调（带 code 参数）

用户完成 Google 授权后，会被重定向到：

```
https://f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de-00-3h1iq9ru0v8kp.sisko.replit.dev/?code=4/0AVGzR1D-xxx...
```

Flask API 自动处理：
- ✅ 提取授权码
- ✅ 换取 access_token
- ✅ 获取用户信息
- ✅ 保存到 Supabase
- ✅ 显示成功页面

### 场景 3：健康检查

```bash
curl https://f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de-00-3h1iq9ru0v8kp.sisko.replit.dev/health
```

**响应：**
```json
{
  "status": "healthy",
  "service": "lynkerai_api",
  "endpoints": {
    "oauth_callback": ["/", "/callback", "/oauth2callback"],
    "api": ["/login_refresh", "/health"]
  }
}
```

---

## 📋 从日志中查看授权记录

从之前的日志可以看到，用户已经尝试过多次授权：

```
172.31.77.162 - - [21/Oct/2025 09:42:36] "GET /?code=4/0AVGzR1Ci5s6RbOZtbmfdqL0WTYyQ9Vk8BGZCJu0LejeZ6KML6M5ICqG7Eudjw7RCv09mkQ... HTTP/1.1" 404 -
172.31.77.162 - - [21/Oct/2025 09:49:23] "GET /?code=4/0AVGzR1D-JRqdcYMn_oDLb8PRTJ3wnLkQckjM7Vgzt7M6d7t--gVegjhwvCpPCIqCTraVYw... HTTP/1.1" 404 -
172.31.77.162 - - [21/Oct/2025 09:52:08] "GET /?code=4/0AVGzR1BPIuQGk3G0FOqMTXF4O1H5mqURL7a0D6yg7C8K9xgnM_4w0s1To1lvH9MgIv_TMw... HTTP/1.1" 404 -
172.31.77.162 - - [21/Oct/2025 09:55:11] "GET /?code=4/0AVGzR1BluNZwI-3ETUP84XcpYwTwB2whfbeM_vMs76dgdzsODLdQjhlSqmxqD86DiU_7PA... HTTP/1.1" 404 -
```

之前返回 404 是因为 Flask API 没有配置 OAuth 回调路由。

**现在已修复！** 新的授权请求会返回 200 并显示成功页面。

---

## 🔄 工作流配置

### 当前配置

```yaml
工作流名称: Flask API
命令: python on_user_login_api.py
端口: 5000
输出类型: webview
状态: ✅ 运行中
```

### 已删除的工作流

- ❌ **OAuth Callback Server** - 已合并到 Flask API

---

## 📁 相关文件

### 核心文件

- **`on_user_login_api.py`** - Flask API 主服务（含 OAuth 回调）
- **`google_oauth_real_flow.py`** - 交互式授权脚本
- **`google_oauth_callback.py`** - 独立的 OAuth 回调服务（已弃用，功能已合并到 Flask API）

### 文档

- **`OAUTH_CALLBACK_GUIDE.md`** - 本文档
- **`OAUTH_TEST_GUIDE.md`** - 测试指南
- **`GOOGLE_OAUTH_USAGE.md`** - OAuth 使用说明

---

## ⚡ 快速开始

### 方式 1：使用交互式脚本（推荐）

```bash
python google_oauth_real_flow.py --user-id=u_demo
```

### 方式 2：直接访问授权 URL

1. 构建授权 URL（或使用脚本生成）
2. 在浏览器中打开
3. 完成授权
4. 自动重定向到 Flask API
5. 查看成功页面

---

## 🎉 集成完成！

Flask API 现在支持：
- ✅ Google OAuth 回调处理
- ✅ 用户登入匹配刷新
- ✅ 健康检查
- ✅ 自动保存到 Supabase
- ✅ 美观的成功页面
- ✅ 单一服务器（5000 端口）

**服务地址：** https://f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de-00-3h1iq9ru0v8kp.sisko.replit.dev/
