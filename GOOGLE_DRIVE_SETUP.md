# ☁️ Google Drive 同步功能 - 设置指南

## 📋 概述

Google Drive 同步功能允许用户将 LynkerAI 的记忆数据备份到个人 Google Drive 云端，确保数据隐私和安全。

---

## 🔧 前置准备

### 1️⃣ 创建 Google Cloud 项目

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 记录项目 ID

### 2️⃣ 启用 Google Drive API

1. 在 Google Cloud Console 中，进入 **API 和服务 > 库**
2. 搜索 "Google Drive API"
3. 点击 **启用**

### 3️⃣ 创建 OAuth 2.0 凭据

1. 进入 **API 和服务 > 凭据**
2. 点击 **创建凭据 > OAuth 客户端 ID**
3. 选择应用类型：**Web 应用**
4. 配置：
   - **名称**：LynkerAI Google Drive Sync
   - **已获授权的 JavaScript 来源**：
     ```
     http://localhost:5000
     https://your-replit-domain.repl.co
     ```
   - **已获授权的重定向 URI**：
     ```
     http://localhost:5000
     https://your-replit-domain.repl.co
     ```
5. 点击 **创建**
6. **复制 客户端 ID**（稍后会用到）

---

## ⚙️ 环境变量配置

在项目根目录创建或编辑 `.env` 文件：

```env
# Google OAuth 配置
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here.apps.googleusercontent.com
VITE_GOOGLE_REDIRECT_URI=https://your-replit-domain.repl.co
```

**注意：**
- `VITE_GOOGLE_CLIENT_ID`：从 Google Cloud Console 复制的客户端 ID
- `VITE_GOOGLE_REDIRECT_URI`：您的应用访问地址（Replit 或本地开发）

---

## 📂 项目文件结构

```
LynkerAI/
├── components/
│   ├── GoogleDriveSyncButton.jsx   # 前端 OAuth 授权按钮
│   └── ChildAIMemoryVault.jsx      # AI 记忆展示组件
├── google_drive_sync.py             # 后端同步模块
├── GOOGLE_DRIVE_SETUP.md            # 本文档
└── .env                             # 环境变量配置
```

---

## 🎨 前端集成

### 使用 GoogleDriveSyncButton 组件

```javascript
import GoogleDriveSyncButton from './components/GoogleDriveSyncButton';
import ChildAIMemoryVault from './components/ChildAIMemoryVault';

function App() {
  const handleAuthSuccess = (token, email) => {
    console.log('✅ Google Drive 授权成功！');
    console.log('Token:', token);
    console.log('Email:', email);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Google Drive 授权按钮 */}
      <GoogleDriveSyncButton onAuthSuccess={handleAuthSuccess} />
      
      {/* AI 记忆仓库 */}
      <ChildAIMemoryVault userId="u_demo" />
    </div>
  );
}
```

---

## 🔧 后端集成

### 使用 google_drive_sync.py 模块

```python
from google_drive_sync import sync_memories_to_drive, test_google_drive_connection

# 1. 测试连接
access_token = "user_google_access_token_from_frontend"
is_connected = test_google_drive_connection(access_token)

# 2. 同步记忆数据
if is_connected:
    memories = [
        {
            "partner_id": "u_test1",
            "summary": "命格高度共振，彼此能深刻理解。",
            "tags": ["设计行业", "晚婚"],
            "similarity": 0.911
        }
    ]
    
    result = sync_memories_to_drive(
        user_id="u_demo",
        memories_data=memories,
        access_token=access_token
    )
    
    print(result)
```

---

## 🔄 工作流程

```
用户点击"绑定 Google Drive"
         ↓
前端跳转到 Google OAuth 授权页面
         ↓
用户授权并返回应用
         ↓
前端接收 access_token 并存储到 localStorage
         ↓
前端调用后端 API 传递 access_token
         ↓
后端使用 google_drive_sync.py 上传数据
         ↓
数据保存到用户的 Google Drive（LynkerAI_Memories 文件夹）
```

---

## 🧪 测试步骤

### 1️⃣ 测试前端授权

1. 启动前端应用
2. 点击 "绑定 Google Drive" 按钮
3. 完成 Google 授权
4. 查看浏览器控制台，确认 access_token 已保存到 localStorage

### 2️⃣ 测试后端同步

```python
# test_google_drive.py
from google_drive_sync import sync_memories_to_drive

# 从前端获取的 access_token
access_token = "YOUR_ACCESS_TOKEN_HERE"

# 测试数据
test_memories = [
    {
        "partner_id": "u_test1",
        "summary": "测试记忆同步",
        "tags": ["测试"],
        "similarity": 0.9
    }
]

# 执行同步
result = sync_memories_to_drive("u_demo", test_memories, access_token)
print(result)
```

### 3️⃣ 验证 Google Drive

1. 登录 [Google Drive](https://drive.google.com/)
2. 查找 "LynkerAI_Memories" 文件夹
3. 确认 JSON 文件已上传

---

## 🔐 安全注意事项

### ✅ 最佳实践

1. **不要硬编码凭据**：始终使用环境变量存储 `GOOGLE_CLIENT_ID`
2. **Token 过期处理**：Google OAuth access_token 通常 1 小时过期，需要实现刷新机制
3. **HTTPS**：生产环境必须使用 HTTPS
4. **最小权限**：仅请求 `drive.file` 范围（只能访问应用创建的文件）

### ⚠️ Token 刷新（可选）

如需长期访问，建议使用 `refresh_token`：

1. 在 OAuth URL 中添加 `access_type=offline`
2. 使用 `response_type=code` 获取 authorization_code
3. 交换 code 获取 refresh_token
4. 存储 refresh_token 到后端数据库

---

## 📊 数据格式

### 上传到 Google Drive 的 JSON 结构

```json
{
  "user_id": "u_demo",
  "timestamp": "20231019_143022",
  "memories_count": 2,
  "data": [
    {
      "partner_id": "u_test1",
      "summary": "命格高度共振，彼此能深刻理解。",
      "tags": ["设计行业", "晚婚", "母缘浅"],
      "similarity": 0.911
    }
  ]
}
```

---

## 🐛 常见问题

### Q1: 授权后没有跳转回应用？
**A**: 检查 Google Cloud Console 中的重定向 URI 是否与实际应用地址完全一致。

### Q2: 上传失败 403 错误？
**A**: 确认已启用 Google Drive API，且 OAuth scope 包含 `drive.file`。

### Q3: Access token 已过期？
**A**: 重新授权或实现 refresh_token 机制。

---

## 📚 参考文档

- [Google Drive API 文档](https://developers.google.com/drive/api/v3/about-sdk)
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)

---

**🎉 设置完成后，用户即可将 AI 记忆安全备份到个人 Google Drive！**
