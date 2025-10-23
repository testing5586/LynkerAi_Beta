# 🚀 LynkerAI Multi-Provider 调度系统 - 快速开始

## 5分钟快速上手

### ✅ 系统已就绪

所有文件已创建并集成到 LynkerAI 系统中！

---

## 📁 文件结构

```
master_ai/
├── provider_manager.py           # 核心调度管理器 ✅
├── provider_test.py              # 测试脚本 ✅
├── provider_stats.json           # 性能统计数据 ✅
├── templates/
│   └── performance.html          # Web 性能面板 ✅
├── README_PROVIDER_MANAGER.md    # 完整文档 ✅
└── QUICK_START.md                # 本文档
```

---

## 🔧 第一步：查看当前性能报告

```bash
cd master_ai
python3 provider_manager.py
```

**输出示例：**
```
======================================================================
  🧠 LynkerAI Multi-Provider 性能报告
======================================================================

📊 总请求数: 0
🕐 最后更新: 无

----------------------------------------------------------------------

🤖 Provider: CHATGPT
   总请求: 0
   成功率: 0.0%
   ...

✨ 推荐 Provider: CHATGPT
======================================================================
```

---

## 🧪 第二步：运行基础测试

```bash
cd master_ai
python3 provider_test.py
```

这将：
1. 发送 3 个测试查询
2. 记录性能数据
3. 生成完整报告

---

## 🌐 第三步：访问 Web 性能面板

系统已自动集成到 Upload API（端口 8008）

访问：**`http://localhost:8008/provider-dashboard`**

您将看到：
- ✅ 实时性能卡片
- ✅ 每个 Provider 的详细统计
- ✅ 成功率可视化
- ✅ 智能推荐
- ✅ 自动刷新（30秒）

---

## 📊 第四步：查看统计 API

```bash
curl http://localhost:8008/api/provider/stats | python3 -m json.tool
```

**返回 JSON 格式的完整统计数据**

---

## 🔥 进阶：压力测试

```bash
cd master_ai

# 运行 10 次测试
python3 provider_test.py stress 10

# 运行 50 次测试
python3 provider_test.py stress 50
```

---

## 🔄 管理统计数据

### 查看报告
```bash
python3 provider_test.py report
```

### 重置统计
```bash
python3 provider_test.py reset
```

---

## 💻 在代码中使用

```python
from master_ai.provider_manager import smart_chat, ProviderManager

# 智能聊天（自动记录性能）
response, provider, time = smart_chat("你好，请介绍一下自己")
print(f"Provider: {provider}, 耗时: {time:.2f}s")

# 获取最佳 Provider
manager = ProviderManager()
best = manager.get_best_provider()
print(f"推荐使用: {best.upper()}")

# 查看详细统计
stats = manager.get_provider_stats("chatgpt")
print(f"成功率: {stats['success_rate']:.1f}%")
```

---

## 🎯 集成到现有系统

### 在 Master Responder 中使用

```python
from master_ai.provider_manager import smart_chat

# 替换原来的调用
response, provider, time = smart_chat(user_message, context="")
print(f"✅ 使用 {provider.upper()}, 耗时 {time:.2f}s")
```

### 在 Flask API 中添加端点

**已自动集成！** ✅

- `/api/provider/stats` - 统计数据 API
- `/provider-dashboard` - Web 性能面板

---

## 📚 完整文档

查看 `README_PROVIDER_MANAGER.md` 了解：
- 详细的 API 说明
- 性能评分算法
- 故障排查指南
- 集成示例

---

## ✨ 特性亮点

✅ **智能调度** - 自动选择最优 Provider  
✅ **性能监控** - 实时跟踪成功率和响应时间  
✅ **自动 Fallback** - 失败时自动切换  
✅ **可视化面板** - 精美的 Web UI  
✅ **统计持久化** - JSON 格式保存数据  
✅ **易于集成** - 无缝接入现有系统  

---

**系统已完全就绪，开始使用吧！** 🎉
