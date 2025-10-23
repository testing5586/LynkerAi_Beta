# 🎯 Superintendent Command Center - 使用指南

## 📌 功能概述

**Lynker Superintendent Command Center (LSCC)** 是 LynkerAI 的管理员控制中心，提供系统监控、数据统计和三方 AI 协作聊天功能。

---

## 🚀 快速访问

### 访问地址

- **主入口**: `https://[your-replit-url]/`
- **直接登录**: `https://[your-replit-url]/admin`

### 访问口令

使用 `MASTER_VAULT_KEY` 的前16位哈希值作为登录密码。

**生成访问令牌**：

```python
import hashlib
import os

MASTER_KEY = os.getenv("MASTER_VAULT_KEY", "default_key")
token = hashlib.sha256(MASTER_KEY.encode()).hexdigest()[:16]
print(f"访问令牌: {token}")
```

**示例**（如果 MASTER_VAULT_KEY = "LynkerAI_MasterVault_2025_SecureKey_v2"）：
```
访问令牌: 9821a9762b008821
```

---

## 📂 系统结构

```
admin_dashboard/
├── app.py                  # Flask 主应用
├── auth.py                 # 身份验证模块
├── chat_hub.py             # AI 协作聊天处理
├── data_fetcher.py         # 数据获取模块
├── templates/
│   ├── login.html          # 登录页面
│   ├── dashboard.html      # 监控仪表板
│   └── chatroom.html       # AI 协作聊天室
└── static/
    └── css/
        └── style.css       # 样式文件
```

---

## 🎛️ 功能模块

### 1️⃣ **登录页面** (`/admin`)

- 🔐 安全的密码验证
- 🎨 现代化渐变背景设计
- 💡 提示信息显示

**访问示例**：
```
http://localhost:5000/admin
```

### 2️⃣ **Dashboard 监控** (`/dashboard`)

#### 实时统计卡片
- **Master AI 状态**: 运行状态监控
- **Group Leaders**: 当前 Leader 数量
- **Child AI 数量**: 子 AI 实例统计
- **Token 消耗**: 今日 Token 使用量

#### 数据库统计
- Master Vault 条目数
- 命盘总数（从 `birthcharts` 表）
- 预测总数（从 `predictions` 表）

#### Token 消耗趋势图
- 使用 Plotly.js 可视化
- 显示每日 Token 使用趋势

#### 最新命理规律发现
- 实时显示 AI 学习成果
- 展示统计规律和洞察

**访问示例**：
```
http://localhost:5000/dashboard
```

### 3️⃣ **AI 协作聊天室** (`/chatroom`)

#### 实时三方协作
- **Master AI 🧠**: 主控分析和总结
- **Group Leader 🧩**: 任务协调
- **Child AI 🤖**: 执行具体分析

#### 功能特性
- 实时 WebSocket 通信（使用 Socket.IO）
- AI 角色状态指示（在线/离线）
- 消息历史记录
- 三方AI自动回复

**访问示例**：
```
http://localhost:5000/chatroom
```

---

## 🖥️ 使用流程

### 步骤 1: 获取访问令牌

在项目根目录运行：

```bash
cd admin_dashboard
python -c "from auth import get_access_token; print('访问令牌:', get_access_token())"
```

### 步骤 2: 访问登录页面

打开浏览器访问主页或直接访问 `/admin`：

```
https://[your-replit-url]/admin
```

### 步骤 3: 输入访问令牌

在登录页面输入上一步获取的16位令牌。

### 步骤 4: 进入 Dashboard

成功登录后自动跳转到监控面板。

### 步骤 5: 探索功能

- 查看实时统计数据
- 浏览 Token 消耗趋势
- 查看最新命理规律发现
- 进入 AI 协作聊天室

---

## 💬 AI 协作聊天使用

### 发送指令

在聊天室输入框中输入命令或提问，例如：

```
分析最近的命盘匹配规律
```

### AI 响应

三方 AI 会依次回复：

```
Master AI 🧠: 我已分析此主题，准备总结核心结论。
Group Leader 🧩: 我将协调下属 AI 执行指令。
Child AI 🤖: 正在执行命盘匹配与规律分析任务...
```

### 实时通信

- 使用 Socket.IO 实现实时双向通信
- 广播消息到所有连接的客户端
- 支持多用户同时在线

---

## 🔧 技术架构

### 后端技术栈

- **Flask**: Python Web 框架
- **Flask-SocketIO**: WebSocket 实时通信
- **Python-SocketIO**: Socket.IO 服务器实现
- **Supabase**: 数据库连接（可选）

### 前端技术栈

- **HTML5 + CSS3**: 页面结构和样式
- **Socket.IO Client**: WebSocket 客户端
- **Plotly.js**: 数据可视化图表
- **Vanilla JavaScript**: 交互逻辑

### 设计特色

- 🎨 现代化渐变设计
- 📱 响应式布局
- 🌙 深色主题配色
- ✨ 流畅动画效果

---

## 📊 数据源

### 实时数据获取

`data_fetcher.py` 从以下数据源获取信息：

1. **Supabase 数据库**（如果配置）：
   - `master_vault` 表 - Vault 条目统计
   - `birthcharts` 表 - 命盘总数
   - `predictions` 表 - 预测总数

2. **模拟数据**（数据库不可用时）：
   - 预设的统计数据
   - 示例命理规律

### 数据更新

- 每次刷新页面时更新
- 实时显示更新时间戳

---

## 🔐 安全机制

### 会话管理

- Flask Session 管理用户登录状态
- Session Secret Key: `lynker_dashboard_session`

### 密码验证

- SHA256 哈希验证
- 使用环境变量 `MASTER_VAULT_KEY`
- 前16位哈希作为访问令牌

### 路由保护

所有受保护路由会检查登录状态：

```python
if not session.get("auth"):
    return redirect("/admin")
```

---

## 🛠️ 开发与调试

### 本地开发

```bash
# 进入目录
cd admin_dashboard

# 运行应用
python app.py
```

### 访问地址

```
http://127.0.0.1:5000
http://0.0.0.0:5000
```

### 调试模式

应用默认开启调试模式：

```python
socketio.run(app, host="0.0.0.0", port=5000, debug=True)
```

**调试功能**：
- 代码修改自动重载
- 详细错误信息
- Debugger PIN 访问

---

## 📈 性能优化

### CORS 配置

```python
socketio = SocketIO(app, cors_allowed_origins="*")
```

### 静态资源

- CSS 文件集中管理
- 使用 CDN 加载外部库（Plotly.js, Socket.IO）

### 数据库连接

- 优雅降级机制
- 数据库不可用时使用模拟数据

---

## 🎨 自定义配置

### 修改端口

编辑 `admin_dashboard/app.py`：

```python
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)
```

### 修改 Session Secret

```python
app.secret_key = "your_custom_secret_key"
```

### 添加新路由

```python
@app.route("/new_page")
def new_page():
    if not session.get("auth"):
        return redirect("/admin")
    return render_template("new_page.html")
```

### 自定义 AI 回复

编辑 `admin_dashboard/chat_hub.py`：

```python
def process_message(message):
    replies = [
        f"{AI_ROLES['master']}: 自定义回复内容...",
        f"{AI_ROLES['leader']}: 自定义回复内容...",
        f"{AI_ROLES['child']}: 自定义回复内容..."
    ]
    return replies
```

---

## 🔄 系统集成

### 与其他模块集成

Admin Dashboard 可以集成以下 LynkerAI 模块：

1. **Master Vault Engine**: 查看加密知识库
2. **Master AI Reasoner**: 显示预测结果
3. **Master AI Scheduler**: 监控自动学习状态
4. **Multi-Model Dispatcher**: 查看模型使用统计

### API 扩展

可以添加 RESTful API 端点：

```python
@app.route("/api/stats")
def api_stats():
    return jsonify(get_dashboard_data())
```

---

## 🐛 故障排查

### 问题 1: 无法访问页面

**可能原因**：
- Workflow 未启动
- 端口 5000 被占用

**解决方法**：
```bash
# 检查 workflow 状态
# 查看日志
cat logs/admin_dashboard.log

# 重启 workflow
# 在 Replit 控制台重启
```

### 问题 2: 登录失败

**可能原因**：
- 访问令牌不正确
- MASTER_VAULT_KEY 未设置

**解决方法**：
```bash
# 检查环境变量
echo $MASTER_VAULT_KEY

# 重新生成令牌
cd admin_dashboard
python -c "from auth import get_access_token; print(get_access_token())"
```

### 问题 3: WebSocket 连接失败

**可能原因**：
- Socket.IO 未正确安装
- CORS 配置问题

**解决方法**：
```bash
# 重新安装依赖
uv sync

# 检查浏览器控制台错误
```

### 问题 4: 数据不显示

**可能原因**：
- Supabase 连接失败
- 数据库表不存在

**解决方法**：
```python
# 测试数据库连接
from data_fetcher import get_dashboard_data
print(get_dashboard_data())
```

---

## 📚 相关文档

- **Master AI Scheduler**: `MASTER_AI_SCHEDULER_GUIDE.md`
- **Multi-Model Dispatcher**: `MULTI_MODEL_DISPATCHER_GUIDE.md`
- **Master Vault Engine**: `master_ai/MASTER_VAULT_ENGINE_GUIDE.md`
- **Master AI Reasoner**: 预测引擎文档

---

## 🎯 路线图

### 即将推出的功能

- [ ] 用户权限管理（多级别访问控制）
- [ ] 实时系统性能监控
- [ ] AI 学习历史记录查看
- [ ] 导出数据报表功能
- [ ] 移动端适配
- [ ] 暗黑/明亮主题切换
- [ ] 高级数据可视化图表
- [ ] AI 协作日志记录

---

## 💡 最佳实践

1. **定期更新访问令牌**
   - 修改 `MASTER_VAULT_KEY` 后重新生成令牌

2. **监控系统状态**
   - 定期查看 Dashboard 统计数据
   - 关注 Token 消耗趋势

3. **使用 AI 协作聊天**
   - 利用三方 AI 协同分析复杂问题
   - 记录重要的 AI 洞察

4. **保护访问安全**
   - 不要在公开场合分享访问令牌
   - 定期更换密钥

---

## ✅ 总结

Superintendent Command Center 提供了：

✅ **实时监控** - 系统状态一目了然  
✅ **数据可视化** - 图表展示 Token 趋势  
✅ **AI 协作** - 三方 AI 实时对话  
✅ **安全访问** - SHA256 哈希验证  
✅ **优雅设计** - 现代化界面体验  
✅ **易于扩展** - 模块化架构设计  

---

**文档版本**: 1.0  
**最后更新**: 2025-10-23  
**维护者**: LynkerAI Team  
**访问地址**: `https://[your-replit-url]/admin`  
**默认端口**: 5000
