# 🧠 LynkerAI Multi-Provider 调度系统 v1.0

## 📋 概述

**LynkerAI Provider Manager** 是一个智能的 AI 提供商调度系统，能够在 **ChatGPT**、**Gemini**、**ChatGLM** 和 **DeepSeek** 四个 AI Provider 之间自动切换，并提供详细的性能统计和可视化面板。

---

## ✨ 核心功能

### 1️⃣ 智能调度
- ✅ 自动在 4 个 Provider 之间切换
- ✅ 基于成功率和响应时间的智能推荐
- ✅ 自动 Fallback 机制（继承自 `multi_model_ai.py`）

### 2️⃣ 性能监控
- ✅ 实时记录每个 Provider 的性能数据
- ✅ 跟踪成功率、响应时间、请求次数
- ✅ JSON 格式持久化存储

### 3️⃣ 可视化面板
- ✅ 精美的 Web UI 性能面板
- ✅ 实时刷新（30秒自动更新）
- ✅ 智能推荐最优 Provider

---

## 📁 文件结构

```
master_ai/
├── provider_manager.py           # 核心调度管理器
├── provider_test.py              # 测试脚本
├── provider_stats.json           # 性能统计数据（自动生成）
├── templates/
│   └── performance.html          # 性能面板 UI
└── README_PROVIDER_MANAGER.md    # 本文档
```

---

## 🚀 快速开始

### 步骤 1: 环境准备

确保已配置 AI Provider 的 API 密钥：

```bash
# Replit Secrets 中配置：
OPENAI_API_KEY=sk-...           # ChatGPT
GEMINI_API_KEY=...              # Google Gemini
GLM_API_KEY=...                 # 智谱 ChatGLM
DEEPSEEK_API_KEY=...            # DeepSeek
```

### 步骤 2: 运行测试

```bash
cd master_ai

# 基础测试（3个查询）
python provider_test.py

# 压力测试（10个请求）
python provider_test.py stress 10

# 查看性能报告
python provider_test.py report

# 重置统计数据
python provider_test.py reset
```

### 步骤 3: 启动性能面板

性能面板需要通过 Flask API 提供：

```python
# 在您的 Flask 应用中添加以下代码：
from master_ai.provider_manager import ProviderManager
from flask import render_template, jsonify

@app.route('/api/provider/stats')
def provider_stats():
    """提供 Provider 统计数据 API"""
    manager = ProviderManager()
    return jsonify(manager.get_all_stats())

@app.route('/provider-dashboard')
def provider_dashboard():
    """性能面板页面"""
    return render_template('performance.html')
```

然后访问：`http://localhost:5000/provider-dashboard`

---

## 💻 使用示例

### 1. 基础调用

```python
from master_ai.provider_manager import smart_chat

# 智能聊天（自动记录性能）
response, provider, time = smart_chat("你好，请介绍一下自己")

print(f"Provider: {provider}")
print(f"响应时间: {time:.2f}s")
print(f"回复: {response}")
```

### 2. 获取性能报告

```python
from master_ai.provider_manager import get_performance_report

# 打印终端报告
print(get_performance_report())
```

### 3. 获取最佳 Provider

```python
from master_ai.provider_manager import ProviderManager

manager = ProviderManager()
best = manager.get_best_provider()
print(f"推荐使用: {best.upper()}")
```

### 4. 查看详细统计

```python
manager = ProviderManager()

# 单个 Provider 统计
chatgpt_stats = manager.get_provider_stats("chatgpt")
print(f"成功率: {chatgpt_stats['success_rate']:.1f}%")

# 所有统计
all_stats = manager.get_all_stats()
```

---

## 📊 性能评分算法

系统使用以下公式计算 Provider 评分：

```python
速度评分 = max(0, 100 - 平均响应时间 * 10)
综合评分 = 成功率 * 0.7 + 速度评分 * 0.3
```

**推荐 Provider** = 综合评分最高的 Provider

---

## 🗂️ 数据格式

`provider_stats.json` 结构：

```json
{
  "providers": {
    "chatgpt": {
      "total_requests": 10,
      "successful_requests": 9,
      "failed_requests": 1,
      "total_response_time": 15.2,
      "avg_response_time": 1.69,
      "success_rate": 90.0,
      "last_used": "2025-10-23T12:00:00",
      "last_status": "成功"
    }
  },
  "total_requests": 40,
  "last_updated": "2025-10-23T12:05:00"
}
```

---

## 🔧 配置选项

### 修改 Fallback 顺序

编辑 `multi_model_ai.py` 中的：

```python
FALLBACK_ORDER = ["chatgpt", "gemini", "glm", "deepseek"]
```

### 修改统计文件路径

```python
manager = ProviderManager(stats_file="custom_path/stats.json")
```

---

## 🎯 测试场景

### 基础功能测试

```bash
python provider_test.py
```

**输出示例：**
```
======================================================================
  🧪 LynkerAI Multi-Provider 测试
======================================================================

📝 测试 1/3: 你好，请简单介绍一下你自己
----------------------------------------------------------------------
🤖 Provider: CHATGPT
⏱️  响应时间: 1.45s
💬 回复: 你好！我是 Lynker Master AI...

✅ 测试完成
```

### 压力测试

```bash
python provider_test.py stress 20
```

### 性能报告

```bash
python provider_test.py report
```

**输出示例：**
```
======================================================================
  🧠 LynkerAI Multi-Provider 性能报告
======================================================================

📊 总请求数: 30
🕐 最后更新: 2025-10-23 12:00:00

----------------------------------------------------------------------

🤖 Provider: CHATGPT
   总请求: 15
   成功率: 93.3%
   平均响应时间: 1.52s
   最后使用: 2025-10-23 12:00:00
   状态: 成功

...

----------------------------------------------------------------------
✨ 推荐 Provider: CHATGPT
======================================================================
```

---

## 🌐 Web 性能面板

访问 `/provider-dashboard` 查看：

- 📊 **实时统计卡片** - 总请求数、最后更新时间
- 🤖 **Provider 性能卡片** - 每个 AI Provider 的详细数据
- 📈 **成功率可视化** - 进度条显示
- ✨ **智能推荐** - 当前最优 Provider
- 🔄 **自动刷新** - 30秒自动更新数据

---

## 🔄 集成到现有系统

### 在 Flask API 中集成

```python
from flask import Flask, jsonify, render_template
from master_ai.provider_manager import ProviderManager, smart_chat

app = Flask(__name__, template_folder='master_ai/templates')

@app.route('/api/provider/stats')
def get_provider_stats():
    manager = ProviderManager()
    return jsonify(manager.get_all_stats())

@app.route('/api/provider/chat', methods=['POST'])
def provider_chat():
    data = request.json
    query = data.get('query', '')
    
    response, provider, time = smart_chat(query)
    
    return jsonify({
        'response': response,
        'provider': provider,
        'response_time': time
    })

@app.route('/provider-dashboard')
def dashboard():
    return render_template('performance.html')
```

### 在 Master Responder 中使用

```python
from master_ai.provider_manager import smart_chat

# 替换原来的 multi_model_chat
response, provider, time = smart_chat(user_message, context, use_rag=True)
print(f"✅ 使用 {provider.upper()}, 耗时 {time:.2f}s")
```

---

## 📈 性能优化建议

1. **定期清理统计数据** - 避免文件过大
   ```bash
   python provider_test.py reset
   ```

2. **监控成功率** - 如果某个 Provider 成功率 < 80%，检查 API 密钥

3. **调整超时设置** - 在 `multi_model_ai.py` 中配置

4. **备份统计数据** - 定期备份 `provider_stats.json`

---

## 🐛 故障排查

### 问题 1: 所有 Provider 都失败

**解决方案：**
```bash
# 检查 API 密钥
python3 verify_secrets.py

# 检查网络连接
curl -I https://api.openai.com
```

### 问题 2: 统计数据不更新

**解决方案：**
```bash
# 检查文件权限
ls -la master_ai/provider_stats.json

# 重新初始化
python provider_test.py reset
```

### 问题 3: Web 面板显示空白

**解决方案：**
1. 确保 Flask API 端点 `/api/provider/stats` 正常工作
2. 检查浏览器控制台错误
3. 确认 `templates/performance.html` 路径正确

---

## 🎉 总结

**LynkerAI Provider Manager** 提供了：

✅ **智能调度** - 自动选择最优 Provider  
✅ **性能监控** - 实时跟踪所有 Provider  
✅ **可视化面板** - 精美的 Web UI  
✅ **易于集成** - 与现有系统无缝对接  

**开始使用：**
```bash
cd master_ai
python provider_test.py
```

**祝您使用愉快！** 🌟
