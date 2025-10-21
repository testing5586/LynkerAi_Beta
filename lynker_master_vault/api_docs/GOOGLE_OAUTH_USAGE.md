# 🔐 Google OAuth 真实授权使用指南

## ✅ 文件说明

**`google_oauth_real_flow.py`** - Google OAuth 2.0 真实授权流程脚本

---

## 🚀 快速开始

### 方法 1：交互式授权（推荐）

```bash
# 运行脚本并指定用户 ID
python google_oauth_real_flow.py --user-id=u_demo
```

**执行步骤：**

1. **脚本会生成授权 URL**
   ```
   ============================================================
   📌 请复制以下链接，在浏览器中打开完成授权：
   ============================================================
   
   https://accounts.google.com/o/oauth2/v2/auth?client_id=...
   ```

2. **在浏览器中打开链接**
   - 选择您的 Google 账号
   - 点击"允许"授权访问 Google Drive
   - 授权后会重定向到：`https://lynkerai.replit.app?code=...`

3. **复制授权码**
   - 从重定向 URL 中复制 `code` 参数的值
   - 例如：`https://lynkerai.replit.app?code=4/0AeanS0ZP...`
   - 复制 `4/0AeanS0ZP...` 这部分

4. **粘贴授权码到终端**
   ```
   🔑 请输入授权码（code 参数的值）：4/0AeanS0ZP...
   ```

5. **脚本自动完成**
   - ✅ 用授权码换取 access_token
   - ✅ 获取用户信息（邮箱）
   - ✅ 保存到 Supabase users 表
   - ✅ 测试 Google Drive 连接

---

## 📋 完整执行流程示例

```bash
$ python google_oauth_real_flow.py --user-id=u_demo

============================================================
🔐 Google OAuth 2.0 真实授权流程
============================================================

📋 Step 1: 读取 OAuth 配置...
✅ Client ID: 85639669324-260ej89u...
✅ Redirect URI: https://lynkerai.replit.app

🔗 Step 2: 生成授权 URL...

============================================================
📌 请复制以下链接，在浏览器中打开完成授权：
============================================================

https://accounts.google.com/o/oauth2/v2/auth?client_id=85639669324-260ej89uej6g4khcb2fj306vk5vgfl28.apps.googleusercontent.com&redirect_uri=https%3A%2F%2Flynkerai.replit.app&response_type=code&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive.file+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+openid&access_type=offline&prompt=consent

============================================================

📝 授权步骤：
   1. 在浏览器中打开上述链接
   2. 选择您的 Google 账号
   3. 点击'允许'授权访问 Google Drive
   4. 授权后会重定向到： https://lynkerai.replit.app
   5. 复制 URL 中的 code 参数值

============================================================

🔑 请输入授权码（code 参数的值）：[在这里粘贴授权码]

🔄 Step 3: 用授权码换取 access_token...
✅ Access Token: ya29.a0AeDClZDFxpZ...
✅ Refresh Token: 1//0gXj7vKZqT8...

👤 Step 4: 获取用户信息...
✅ 用户邮箱：user@gmail.com
✅ 用户名称：Demo User

💾 Step 5: 保存到 Supabase (user_id: u_demo)...
✅ 成功保存到 Supabase users 表！

🧪 Step 6: 测试 Google Drive 连接...
✅ Google Drive 连接成功！用户：user@gmail.com
✅ Google Drive 连接测试成功！

============================================================
🎉 OAuth 授权流程完成！
============================================================

📊 下一步操作：
   1. 生成子AI记忆：python child_ai_memory.py
   2. 记忆会自动同步到 Google Drive
```

---

## 🔧 命令参数

### 基本语法

```bash
python google_oauth_real_flow.py [选项]
```

### 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `--user-id` | 用户ID（保存到 Supabase） | `--user-id=u_demo` |

### 使用示例

```bash
# 为用户 u_demo 授权
python google_oauth_real_flow.py --user-id=u_demo

# 为用户 u_alice 授权
python google_oauth_real_flow.py --user-id=u_alice

# 仅测试授权流程（不保存）
python google_oauth_real_flow.py
```

---

## 📊 授权后的数据存储

**Supabase `users` 表会更新以下字段：**

```sql
UPDATE users SET
  drive_connected = TRUE,
  drive_access_token = 'ya29.a0AeDClZD...',
  drive_refresh_token = '1//0gXj7vKZq...',
  drive_email = 'user@gmail.com'
WHERE name = 'u_demo';
```

---

## 🔐 授权范围说明

脚本请求以下 Google API 权限：

| 权限范围 | 说明 |
|---------|------|
| `drive.file` | 访问应用创建的文件 |
| `userinfo.email` | 读取用户邮箱地址 |
| `openid` | 基础身份验证信息 |

**安全说明：**
- ✅ 只能访问应用自己创建的文件
- ✅ 无法访问用户其他 Google Drive 文件
- ✅ 符合最小权限原则

---

## 🧪 测试场景

### 场景 1：首次绑定

```bash
python google_oauth_real_flow.py --user-id=u_demo
```

**预期结果：**
- ✅ 生成授权 URL
- ✅ 用户完成授权
- ✅ 获取 access_token
- ✅ 保存到 Supabase
- ✅ drive_connected = TRUE

### 场景 2：重新授权

```bash
python google_oauth_real_flow.py --user-id=u_demo
```

**预期结果：**
- ✅ 覆盖旧的 access_token
- ✅ 更新 refresh_token
- ✅ 保持 drive_connected = TRUE

### 场景 3：测试授权（不保存）

```bash
python google_oauth_real_flow.py
```

**预期结果：**
- ✅ 生成授权 URL
- ✅ 获取 access_token
- ✅ 测试 Google Drive 连接
- ⚠️ 不保存到 Supabase

---

## ⚠️ 常见问题

### Q1: 授权后重定向到 404 页面？

**A:** 这是正常现象！重定向地址可能还没有对应的页面。
- 只需复制浏览器地址栏的 URL
- 提取 `code` 参数值即可

### Q2: Token 交换失败？

**可能原因：**
1. 授权码已使用（每个 code 只能用一次）
2. 授权码已过期（10分钟有效期）
3. Client Secret 配置错误

**解决方法：**
1. 重新运行脚本生成新的授权 URL
2. 重新授权获取新的 code
3. 检查 Replit Secrets 中的配置

### Q3: 保存到 Supabase 失败？

**可能原因：**
1. users 表不存在 drive_* 字段
2. user_id 在 users 表中不存在

**解决方法：**
```bash
# 运行自动修复脚本
python fix_supabase_users_schema.py
```

---

## 📈 授权完成后

### 自动同步到 Google Drive

```bash
# 生成子AI记忆（会自动同步）
python child_ai_memory.py
```

**输出示例：**
```
✅ 记忆同步完成：新建 5 条，更新 3 条
☁️ 正在上传子AI记忆到 Google Drive ...
✅ 找到已存在的文件夹：LynkerAI_Memories
✅ 文件已上传到 Google Drive：lynker_ai_memories_u_demo_20251019.json
✅ Google Drive 同步成功！
```

### 手动同步到 Google Drive

```python
from google_drive_sync import auto_sync_user_memories

result = auto_sync_user_memories("u_demo")
```

---

## 🔄 Token 刷新机制

**Access Token 有效期：** 1 小时

**Refresh Token：** 长期有效（可用于获取新的 access_token）

**未来优化建议：**
- 实现自动 token 刷新
- 检测 token 过期并自动刷新
- 避免用户频繁重新授权

---

## 📚 相关文件

- **`google_oauth_real_flow.py`** - 真实授权流程脚本
- **`google_drive_sync.py`** - Google Drive 同步模块
- **`child_ai_memory.py`** - 子AI记忆模块（含自动同步）
- **`fix_supabase_users_schema.py`** - 自动修复表结构
- **`verify_google_oauth_config.py`** - OAuth 配置验证

---

**🎉 现在可以使用真实的 Google OAuth 授权了！**
