# 🔐 Google OAuth 真实授权流程 - 完整指南

## ✅ 环境配置验证

所有必需的 Google OAuth 密钥已在 Replit Secrets 中配置：

| 密钥 | 状态 | 描述 |
|------|------|------|
| `VITE_GOOGLE_CLIENT_ID` | ✅ 已配置 | OAuth 客户端 ID |
| `VITE_GOOGLE_CLIENT_SECRET` | ✅ 已配置 | OAuth 客户端密钥 |
| `VITE_GOOGLE_REDIRECT_URI` | ✅ 已配置 | 授权回调地址 |

---

## 🔗 OAuth 授权 URL

用户需要访问以下链接完成 Google 账号授权：

```
https://accounts.google.com/o/oauth2/v2/auth?client_id=85639669324-260ej89uej6g4khcb2fj306vk5vgfl28.apps.googleusercontent.com&redirect_uri=https://lynkerai.replit.app&response_type=code&scope=https://www.googleapis.com/auth/drive.file&access_type=offline&prompt=consent
```

---

## 📋 完整授权流程

### 🎯 前端流程（React 组件）

**1️⃣ 用户点击绑定按钮**

```jsx
import GoogleDriveSyncButton from './components/GoogleDriveSyncButton';

<GoogleDriveSyncButton 
  onAuthSuccess={(accessToken) => {
    console.log('授权成功！Token:', accessToken);
  }}
/>
```

**2️⃣ 组件生成授权链接并跳转**

```javascript
const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;
const REDIRECT_URI = import.meta.env.VITE_GOOGLE_REDIRECT_URI;

const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
  `client_id=${CLIENT_ID}&` +
  `redirect_uri=${REDIRECT_URI}&` +
  `response_type=code&` +
  `scope=https://www.googleapis.com/auth/drive.file&` +
  `access_type=offline&` +
  `prompt=consent`;

window.location.href = authUrl;
```

**3️⃣ 用户在 Google 页面授权**

- 选择 Google 账号
- 确认授权 "访问 Google Drive 文件"
- 点击"允许"

**4️⃣ Google 重定向回应用**

```
https://lynkerai.replit.app?code=4/0AeanS0ZP...（授权码）
```

**5️⃣ 前端用 code 换取 access_token**

```javascript
// 后端 API：/api/google-auth/exchange-token
const response = await fetch('/api/google-auth/exchange-token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    code: authCode,
    user_id: currentUserId
  })
});

const { access_token } = await response.json();
```

---

### 🐍 后端流程（Flask API）

**创建 Token 交换端点：**

```python
from flask import Flask, request, jsonify
import requests
import os
from supabase_init import init_supabase

app = Flask(__name__)

@app.route('/api/google-auth/exchange-token', methods=['POST'])
def exchange_token():
    """用授权码换取 access_token"""
    
    data = request.json
    auth_code = data.get('code')
    user_id = data.get('user_id')
    
    if not auth_code or not user_id:
        return jsonify({'error': '缺少必需参数'}), 400
    
    # 1. 用 code 换取 access_token
    token_url = 'https://oauth2.googleapis.com/token'
    
    token_data = {
        'code': auth_code,
        'client_id': os.getenv('VITE_GOOGLE_CLIENT_ID'),
        'client_secret': os.getenv('VITE_GOOGLE_CLIENT_SECRET'),
        'redirect_uri': os.getenv('VITE_GOOGLE_REDIRECT_URI'),
        'grant_type': 'authorization_code'
    }
    
    response = requests.post(token_url, data=token_data)
    
    if response.status_code != 200:
        return jsonify({'error': 'Token 交换失败'}), 400
    
    token_info = response.json()
    access_token = token_info.get('access_token')
    refresh_token = token_info.get('refresh_token')
    
    # 2. 获取用户邮箱
    user_info_response = requests.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    user_email = user_info_response.json().get('email')
    
    # 3. 存储到 Supabase users 表
    supabase = init_supabase()
    
    supabase.table('users').update({
        'drive_connected': True,
        'drive_access_token': access_token,
        'drive_refresh_token': refresh_token,  # 可选：用于长期访问
        'drive_email': user_email
    }).eq('name', user_id).execute()
    
    return jsonify({
        'success': True,
        'access_token': access_token,
        'email': user_email
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## 🔄 自动同步流程

**用户绑定 Google Drive 后，子AI记忆会自动同步：**

```python
# child_ai_memory.py 已集成自动同步

from google_drive_sync import auto_sync_user_memories

# 生成记忆后自动同步
count = batch_create_memories_from_insights(user_id, supabase)

# ☁️ 自动同步到 Google Drive
# ✅ Google Drive 同步成功！
```

**同步逻辑：**

1. 检查用户是否绑定（`drive_connected = TRUE`）
2. 读取 `access_token`
3. 从 `child_ai_memory` 表读取记忆数据
4. 上传到 Google Drive "LynkerAI_Memories" 文件夹

---

## 🧪 测试流程

### 1️⃣ 验证配置

```bash
python verify_google_oauth_config.py
```

**预期输出：**
```
✅ Google OAuth Client ID
✅ Google OAuth Client Secret
✅ Google OAuth Redirect URI
🎉 所有 Google OAuth 密钥配置正确！
```

### 2️⃣ 启动 Flask API

```bash
python on_user_login_api.py
```

### 3️⃣ 前端集成组件

```jsx
// 在您的前端页面中
import GoogleDriveSyncButton from './components/GoogleDriveSyncButton';

function UserProfile() {
  return (
    <div>
      <h2>绑定 Google Drive</h2>
      <GoogleDriveSyncButton 
        onAuthSuccess={(token) => {
          alert('绑定成功！');
        }}
      />
    </div>
  );
}
```

### 4️⃣ 用户点击按钮测试

1. 用户点击"绑定 Google Drive"按钮
2. 跳转到 Google 授权页面
3. 选择账号并授权
4. 重定向回应用
5. 后端自动存储 token 到 Supabase
6. 前端显示"绑定成功"

---

## 🔐 安全说明

1. **Client Secret 保护**
   - ✅ 存储在 Replit Secrets（加密）
   - ✅ 仅后端使用，不暴露给前端
   - ❌ 绝不提交到 Git

2. **Access Token 管理**
   - ✅ 存储在 Supabase `users` 表
   - ✅ 仅服务器端使用
   - ⚠️ Token 有效期 1 小时（建议实现 refresh_token）

3. **权限范围**
   - ✅ 仅请求 `drive.file` 权限
   - ✅ 只能访问应用创建的文件
   - ❌ 无法访问用户其他 Google Drive 文件

---

## 📊 数据流向

```
用户点击绑定
     ↓
Google 授权页面
     ↓
用户授权
     ↓
重定向回应用（带 code）
     ↓
后端用 code 换 access_token
     ↓
存储到 Supabase users 表
     ├─ drive_connected = TRUE
     ├─ drive_access_token = token
     └─ drive_email = email
     ↓
子AI记忆自动同步到 Google Drive
```

---

## 🎯 下一步行动

### 短期（开发测试）

- [x] ✅ 配置 Google OAuth 密钥
- [x] ✅ 验证配置正确性
- [ ] 创建 Flask API 端点（`/api/google-auth/exchange-token`）
- [ ] 前端集成 `GoogleDriveSyncButton.jsx` 组件
- [ ] 使用真实 Google 账号测试授权流程

### 中期（功能完善）

- [ ] 实现 refresh_token 机制（长期访问）
- [ ] 添加绑定状态显示（前端 UI）
- [ ] 添加解绑功能
- [ ] 错误处理和重试逻辑

### 长期（生产优化）

- [ ] 增量同步（避免重复上传）
- [ ] 后台任务队列（异步同步）
- [ ] 同步历史记录
- [ ] 用户 Dashboard（查看同步状态）

---

**🎉 Google OAuth 配置完成！现在可以开始集成真实授权流程了！**
