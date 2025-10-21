# 🔄 自动检测域名并更新重定向 URI 指南

## ✅ 脚本已创建

**文件：** `update_redirect_uri.py`

---

## 🚀 快速开始

### 运行脚本

```bash
python update_redirect_uri.py
```

### 预期输出

```
============================================================
🔐 Replit OAuth 重定向 URI 自动更新工具
============================================================

🔍 Step 1: 检测 Replit 域名...
✅ 检测到域名：https://f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de-00-3h1iq9ru0v8kp.sisko.replit.dev

🔍 Step 2: 检查域名可访问性...
✅ 域名可访问

============================================================
🔍 域名检测结果
============================================================

📌 当前重定向 URI:
   https://f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de-00-3h1iq9ru0v8kp.sisko.replit.dev/

✅ 建议的重定向 URI:
   https://f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de-00-3h1iq9ru0v8kp.sisko.replit.dev/

============================================================
📝 更新步骤
============================================================

✅ 当前配置正确，无需更新！
```

---

## 🔧 核心功能

### 1️⃣ 自动检测域名

脚本使用以下方法检测 Replit 域名（优先级从高到低）：

```python
# 方法 1: REPLIT_DOMAINS 环境变量
REPLIT_DOMAINS = "f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de-00-3h1iq9ru0v8kp.sisko.replit.dev"

# 方法 2: REPLIT_DEV_DOMAIN 环境变量
REPLIT_DEV_DOMAIN = "..."

# 方法 3: 从 REPL_ID 构建 Sisko 域名
REPL_ID = "f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de"
→ 构建为：https://f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de.sisko.replit.dev

# 方法 4: 从 REPL_SLUG 和 REPL_OWNER 构建传统域名
REPL_SLUG = "my-repl"
REPL_OWNER = "username"
→ 构建为：https://my-repl.username.repl.co
```

### 2️⃣ 域名可访问性检查

脚本会尝试访问以下端点来验证域名：

```python
# 首选：健康检查端点
GET https://{domain}/health

# 备选：根路径
GET https://{domain}/
```

### 3️⃣ 对比当前配置

```python
current_uri = os.getenv('VITE_GOOGLE_REDIRECT_URI')
suggested_uri = detect_domain() + "/"

if current_uri == suggested_uri:
    print("✅ 配置正确，无需更新")
else:
    print("⚠️ 需要更新")
```

---

## 📋 使用场景

### 场景 1：首次设置

**情况：** 首次配置 OAuth，需要设置重定向 URI

**运行脚本：**
```bash
python update_redirect_uri.py
```

**按照提示操作：**
1. 查看检测到的域名
2. 复制建议的重定向 URI
3. 在 Replit Secrets 中设置
4. 在 Google Cloud Console 中添加

### 场景 2：域名变更

**情况：** Replit 分配了新的 Sisko 域名

**运行脚本：**
```bash
python update_redirect_uri.py
```

**自动检测新域名：**
- 脚本会自动检测新的 Sisko 域名
- 提示您更新配置

### 场景 3：验证配置

**情况：** 想检查当前配置是否正确

**运行脚本：**
```bash
python update_redirect_uri.py
```

**查看对比结果：**
- 当前配置的 URI
- 建议的 URI
- 是否需要更新

---

## 🎯 交互式选项

脚本运行后提供以下选项：

### 选项 A：手动更新（推荐）

```
请选择 (A/B/C) 或按 Enter 退出：A

✅ 请按照上述步骤手动更新重定向 URI
```

**更新步骤：**

1. **更新 Replit Secrets**
   - 在 Replit 左侧菜单点击 'Secrets' (🔒)
   - 找到 `VITE_GOOGLE_REDIRECT_URI`
   - 更新为脚本建议的值

2. **更新 Google Cloud Console**
   - 访问：https://console.cloud.google.com/
   - 进入 'APIs & Services' → 'Credentials'
   - 点击您的 OAuth 2.0 客户端 ID
   - 在 'Authorized redirect URIs' 中添加新 URI

3. **重启服务**
   - 更新完成后，重启 Flask API workflow

### 选项 B：复制重定向 URI

```
请选择 (A/B/C) 或按 Enter 退出：B

============================================================
📋 请复制以下 URI：
============================================================

https://f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de-00-3h1iq9ru0v8kp.sisko.replit.dev/

============================================================
```

**方便复制粘贴**，避免手动输入错误。

### 选项 C：查看环境变量详情

```
请选择 (A/B/C) 或按 Enter 退出：C

============================================================
📊 环境变量详情
============================================================

REPLIT_DOMAINS: f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de-00-3h1iq9ru0v8kp.sisko.replit.dev
REPLIT_DEV_DOMAIN: NOT_SET
REPL_ID: f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de
REPL_SLUG: lynkerai
REPL_OWNER: kynn75
VITE_GOOGLE_CLIENT_ID: 85639669324-260ej89u...
VITE_GOOGLE_REDIRECT_URI: https://...
```

**调试用途**，查看所有相关环境变量。

---

## 🔐 安全说明

### 为什么不自动更新？

**1. 不修改 .env 文件**
- .env 文件不应该被程序自动修改
- 可能导致版本控制冲突
- Replit Secrets 是推荐的方式

**2. 不自动调用 Google API**
- 需要额外的服务账号凭证
- 存在安全风险
- 手动更新更安全、更可靠

### 推荐做法

✅ **使用 Replit Secrets**
- 在 Replit UI 中手动管理
- 自动加密存储
- 不会提交到代码库

✅ **手动更新 Google Cloud Console**
- 直观的 Web 界面
- 可以查看历史记录
- 更安全的权限管理

---

## 📊 检测逻辑流程图

```
开始
  ↓
读取 REPLIT_DOMAINS 环境变量
  ↓
存在? ──否→ 尝试读取 REPLIT_DEV_DOMAIN
  |           ↓
 是          存在? ──否→ 从 REPL_ID 构建
  ↓           |           ↓
使用此域名 ←─是        存在? ──否→ 从 REPL_SLUG + REPL_OWNER 构建
  ↓                       |           ↓
添加 https:// 前缀 ←─────是        存在? ──否→ 无法检测
  ↓                                   |
添加 / 后缀                          是
  ↓                                   ↓
建议的重定向 URI ←──────────────────┘
  ↓
与当前配置对比
  ↓
显示更新指南
  ↓
结束
```

---

## 🧪 测试场景

### 测试 1：正常检测

```bash
$ python update_redirect_uri.py

✅ 检测到域名：https://xxx.sisko.replit.dev
✅ 域名可访问
✅ 当前配置正确，无需更新！
```

### 测试 2：需要更新

```bash
$ python update_redirect_uri.py

✅ 检测到域名：https://new-domain.sisko.replit.dev
⚠️ 域名暂时无法访问

📌 当前重定向 URI:
   https://old-domain.sisko.replit.dev/

✅ 建议的重定向 URI:
   https://new-domain.sisko.replit.dev/

🔧 请按以下步骤更新重定向 URI...
```

### 测试 3：查看环境变量

```bash
$ python update_redirect_uri.py
# 选择 C

📊 环境变量详情
REPLIT_DOMAINS: xxx.sisko.replit.dev
REPL_ID: xxx
...
```

---

## 🔄 集成到工作流

### 定期检查（可选）

创建一个简单的检查脚本：

```bash
#!/bin/bash
# check_redirect_uri.sh

echo "🔍 检查 OAuth 重定向 URI..."
python update_redirect_uri.py | grep "当前配置正确"

if [ $? -eq 0 ]; then
    echo "✅ 配置正确"
    exit 0
else
    echo "⚠️ 配置需要更新"
    python update_redirect_uri.py
    exit 1
fi
```

### 在部署前运行

```bash
# 部署前检查
python update_redirect_uri.py

# 如果需要更新，先更新再部署
# 否则直接部署
```

---

## 📚 相关文件

- **`update_redirect_uri.py`** - 主脚本
- **`on_user_login_api.py`** - Flask API（包含 OAuth 回调）
- **`google_oauth_real_flow.py`** - 交互式授权脚本
- **`OAUTH_CALLBACK_GUIDE.md`** - OAuth 回调指南

---

## 🎉 总结

**脚本功能：**
- ✅ 自动检测 Replit 域名
- ✅ 验证域名可访问性
- ✅ 对比当前配置
- ✅ 提供详细更新指南
- ✅ 交互式操作选项

**安全考虑：**
- ✅ 不自动修改文件
- ✅ 不自动调用 API
- ✅ 推荐手动更新

**使用简单：**
```bash
python update_redirect_uri.py
```

**🎯 准备就绪！运行脚本开始检测和更新重定向 URI！**
