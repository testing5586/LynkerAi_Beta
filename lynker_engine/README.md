# Lynker Engine v2.0

## 🧠 核心架构 (Core Architecture)

Lynker Engine 采用三层 AI 协作架构：
Lynker Engine uses a three-layer AI collaborative architecture:

```
Superintendent (总控)
    ↓
Group Leader (分组领导)
    ↓
Master AI (主推理引擎)
```

## 📁 模块结构 (Module Structure)

```
lynker_engine/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── master_ai.py      # Master AI 推理核心
│   ├── group_leader.py   # Group Leader 协调层
│   ├── superintendent.py # Superintendent 总控层
│   └── superintendent_db.py # Superintendent 数据库版
└── README.md
```

## 🚀 快速开始 (Quick Start)

### 运行 Master AI 测试 (Run Master AI Test)
```bash
python -m lynker_engine.core.master_ai
```

### 运行 Group Leader 测试 (Run Group Leader Test)
```bash
python -m lynker_engine.core.group_leader
```

### 运行 Superintendent 测试 (Run Superintendent Test)
```bash
python -m lynker_engine.core.superintendent
```

### 运行 Superintendent 数据库版测试 (Run Superintendent DB Test)
```bash
python -m lynker_engine.core.superintendent_db
```

### 在应用中集成 (Integrate in Application)
```python
from lynker_engine.core.master_ai import run_master_ai
from lynker_engine.core.group_leader import run_group_leader
from lynker_engine.core.superintendent import run_superintendent
from lynker_engine.core.superintendent_db import run_superintendent_db

# 准备任务载荷
task_payload = {
    "topic": "对照分析：天府 vs 武曲",
    "bazi_result": {"summary": "天府命格稳健"},
    "ziwei_result": {"summary": "武曲守财命"},
    "group_notes": "来自 Group Leader"
}

# 执行 Master AI 推理
result = run_master_ai(task_payload)
print(result)

# 准备子 AI 输出
child_outputs = {
    "bazi_child": {...},
    "ziwei_child": {...}
}

# 执行 Group Leader 协调
group_result = run_group_leader("对照分析", child_outputs)
print(group_result)

# 执行完整四层架构
superintendent_result = run_superintendent("对比天府坐命与武曲守财两类命盘")
print(superintendent_result)

# 执行数据库版架构
superintendent_db_result = run_superintendent_db("1", "验证天府坐命与武曲守财命盘的真实度与预期差异")
print(superintendent_db_result)
```

## 🔧 功能特性 (Features)

### ✅ 四层协作架构
- **Superintendent**: 顶层指挥和任务分发
- **Child AI**: 专门化命盘分析（模拟）
- **Group Leader**: 协调多个子 AI 输出
- **Master AI**: 深度推理和模式识别
- **数据流**: Child AI → Group Leader → Master AI → Superintendent

### ✅ 数据库集成
- **Supabase 连接**: 自动读取最新验证记录
- **数据回退**: 当数据库无记录时使用模拟数据
- **环境变量**: 自动加载 .env 配置
- **错误处理**: 完善的数据库连接异常处理

### ✅ 智能任务识别
- 对照分析 → compare_mode
- 时间流年 → timeline_mode
- 宫位统计 → structure_mode
- 通用任务 → generic_mode

### ✅ 双层推理机制
- **深度推理**: 完整的 AI 分析流程
- **安全回退**: 当主模型不可用时的基础推理

### ✅ 子 AI 输出标准化
- 自动格式化不同子 AI 的输出
- 统一置信度和证据结构
- 冲突检测和汇总

### ✅ 顶层任务协调
- 自动分发任务到各个子 AI
- 协调多个分析流程
- 生成最终综合报告

### ✅ JSON 安全输出
- 自动处理 Unicode 编码
- 结构化数据返回
- 错误容错机制

## 📊 支持的分析模式 (Supported Analysis Modes)

### 1. 对照分析 (Compare Analysis)
比较两个命盘的核心特征差异：
Compare core feature differences between two birth charts:

```json
{
  "核心对比": {
    "婚姻稳定率": "天府命婚姻稳：87% vs 武曲命：71%",
    "财富峰值年龄": "38 vs 32",
    "化禄化忌同时率": "22% vs 35%"
  },
  "结论": "天府命更偏向稳定积累..."
}
```

### 2. 时间回测 (Timeline Analysis)
预测关键人生节点：
Predict key life milestones:

```json
{
  "核心节点": [
    {"年份": "25岁", "八字提示": "事业启动", "紫微提示": "迁移宫动"},
    {"年份": "35岁", "八字提示": "财旺", "紫微提示": "大限合禄"}
  ],
  "结论": "两命时间走势一致度约 80%..."
}
```

### 3. 宫位结构 (Structure Analysis)
统计命盘结构特征：
Analyze birth chart structure:

```json
{
  "统计指标": {
    "命宫主星": "天府",
    "财帛宫主星": "武曲",
    "化禄星比例": "65% vs 58%"
  },
  "结论": "命宫与财帛宫星曜能量分布平衡..."
}
```

## 🔄 与现有系统集成 (Integration with Existing System)

### 在 Admin Dashboard 中使用
```python
# 在 admin_dashboard/lynker_engine.py 中集成
from lynker_engine.core.master_ai import run_master_ai

def process_query(user_query):
    # 现有逻辑...
    
    # 调用 Master AI
    if "对照" in user_query or "比较" in user_query:
        result = run_master_ai({
            "topic": user_query,
            "bazi_result": bazi_data,
            "ziwei_result": ziwei_data,
            "group_notes": "来自 Superintendent"
        })
        return result["summary"]["结论"]
```

### 在 Chat Hub 中使用
```python
# 在 admin_dashboard/chat_hub_v2.py 中集成
from lynker_engine.core.master_ai import run_master_ai

def process_message(message):
    if "命盘" in message:
        # 提取命盘数据...
        result = run_master_ai(task_payload)
        return result["summary"]
```

## 🛠️ 扩展开发 (Extension Development)

### 添加新的分析模式
```python
# 在 master_ai.py 中添加新函数
def new_analysis_mode(bazi, ziwei):
    return {
        "新指标": "...",
        "结论": "..."
    }

# 在 deep_inference 中添加条件判断
elif "新关键词" in topic:
    mode = "new_mode"
```

### 自定义数据源
```python
# 支持扩展数据格式
task_payload = {
    "topic": "自定义分析",
    "bazi_result": {...},
    "ziwei_result": {...},
    "western_result": {...},  # 西方占星
    "group_notes": "..."
}
```

## 📝 日志和调试 (Logging & Debug)

Master AI 内置日志系统：
Master AI has built-in logging system:

```python
# 日志输出格式
[16:58:32] MasterAI> 开始深度推理任务: 对照分析
[16:58:32] MasterAI> 正在执行 deep_inference() ...
[16:58:32] MasterAI> ✅ 深度推理完成
```

## 🔮 未来规划 (Future Roadmap)

- [ ] 支持更多命理体系 (Western, Vedic)
- [ ] 机器学习模型集成
- [ ] 实时协作推理
- [ ] 可视化分析报告
- [ ] API 接口标准化

---

**Lynker Engine v2.0** - 智能命理推理核心
Intelligent Birth Chart Analysis Core