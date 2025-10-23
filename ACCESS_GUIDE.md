# 🌐 LynkerAI Provider Dashboard 访问指南

## ⚠️ 重要：Replit 环境访问说明

在 Replit 云环境中，**您不能使用 localhost 访问应用**。

---

## ✅ 正确的访问方式

### Provider 性能面板

**完整 URL：**
```
https://f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de-00-3h1iq9ru0v8kp.sisko.replit.dev/provider-dashboard
```

**简化访问步骤：**
1. 点击 Replit 界面右上角的 **Webview 窗口**
2. 在地址栏添加路径：`/provider-dashboard`
3. 按 Enter 访问

---

### API 统计数据端点

**完整 URL：**
```
https://f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de-00-3h1iq9ru0v8kp.sisko.replit.dev/api/provider/stats
```

---

## 🔍 其他可用端点

| 端点 | 访问路径 | 功能 |
|------|----------|------|
| 主页 | `/` | OAuth 回调页面 |
| RAG 聊天 | `/chat` | 智能问答界面 |
| Memory Dashboard | `/master-ai-memory` | Child AI 记忆面板 |
| **Provider Dashboard** | `/provider-dashboard` | **多模型性能面板** ⭐ |
| 三方聊天 | `/tri-chat` | 三方对话界面 |
| 健康检查 | `/health` | 系统状态 |

---

## 💡 为什么不能用 localhost？

在 Replit 中：
- ✅ 应用运行在**云服务器**上（不是您的本地电脑）
- ✅ 每个 Repl 都有**唯一的公共 URL**
- ❌ `localhost:5000` 指向**您的本地电脑**，而不是 Replit 服务器

---

## 🚀 快速访问

直接点击下面的链接（在 Replit 中）：

**🔗 Provider Dashboard:**
`/provider-dashboard`

**🔗 API Stats:**
`/api/provider/stats`

---

**提示：** 将您的 Replit URL 保存为书签，方便以后访问！
