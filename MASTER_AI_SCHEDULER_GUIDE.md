# 🤖 Master AI Scheduler 使用指南

## 📌 功能概述

`master_ai_scheduler.py` 是 LynkerAI 的自动定时学习系统，定期运行 Evolution Engine 和 Reasoner 模块，实现 Master AI 的自主学习和知识积累。

---

## 🎯 核心功能

### 1️⃣ **自动化学习流程**

每隔 N 天（默认7天）自动执行：

1. **Evolution Engine** - 分析命盘数据，提炼规律
2. **Reasoner Engine** - 为所有用户生成预测
3. **Master Vault** - 加密存储学习成果

### 2️⃣ **智能配置管理**

- 从 `ai_rules` 表动态加载训练周期
- 支持热更新（修改数据库配置即生效）
- 灵活调整学习频率

### 3️⃣ **完整日志追踪**

- 详细记录每次执行过程
- 保存到 `logs/master_ai_scheduler.log`
- 包含时间戳、状态、错误信息

---

## 🚀 快速开始

### 启动调度器

```bash
python master_ai_scheduler.py
```

### 后台运行（Linux/Mac）

```bash
nohup python master_ai_scheduler.py > scheduler_output.log 2>&1 &
```

### 查看日志

```bash
tail -f logs/master_ai_scheduler.log
```

### 停止调度器

```bash
# 找到进程 ID
ps aux | grep master_ai_scheduler

# 终止进程
kill <PID>
```

---

## ⚙️ 配置管理

### 查看当前配置

```python
from multi_model_dispatcher import load_ai_rules

rules = load_ai_rules()
print(f"训练周期: {rules['TRAINING_INTERVAL_DAYS']} 天")
```

### 修改训练周期

#### 方法 1: 通过 SQL（推荐）

```sql
-- 修改为每3天训练一次
UPDATE ai_rules 
SET rule_value = '3' 
WHERE rule_name = 'TRAINING_INTERVAL_DAYS';
```

#### 方法 2: 通过 Python

```python
from supabase import create_client
import os

client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

client.table("ai_rules").update({
    "rule_value": "3",
    "updated_at": "now()",
    "updated_by": "admin"
}).eq("rule_name", "TRAINING_INTERVAL_DAYS").execute()

print("✅ 训练周期已更新为 3 天")
```

**注意**：修改后需重启调度器才能生效。

---

## 📊 工作流程

```
调度器启动
  ↓
加载配置 (ai_rules 表)
  ↓
设置定时任务 (每 N 天)
  ↓
立即执行首次学习
  ↓
┌──────────────────────────┐
│  阶段 1: Evolution Engine │
│  - 读取 birthcharts 表    │
│  - 分析命盘规律          │
│  - 提炼统计特征          │
│  - 加密存入 Vault        │
└──────────────────────────┘
  ↓
┌──────────────────────────┐
│  阶段 2: Reasoner Engine  │
│  - 为前100位用户推理     │
│  - 整合多源数据          │
│  - 生成预测结果          │
│  - 存入 predictions 表   │
└──────────────────────────┘
  ↓
┌──────────────────────────┐
│  阶段 3: Master Vault     │
│  - 创建学习纪要          │
│  - AES256 加密           │
│  - 存入 master_vault 表  │
└──────────────────────────┘
  ↓
写入日志
  ↓
等待下次执行 (N 天后)
  ↓
循环...
```

---

## 📝 日志示例

### 正常执行日志

```log
============================================================
[2025-10-23 12:00:00] 🚀 Master AI 自学习启动 | 训练周期: 7 天
============================================================

[2025-10-23 12:00:01] 📊 阶段 1/3: Evolution Engine - 提炼命盘规律...
[2025-10-23 12:01:30] ✅ Evolution Engine 完成

[2025-10-23 12:01:31] 🧠 阶段 2/3: Reasoner - 全量用户推理（前100位）...
[2025-10-23 12:05:45] ✅ Reasoner 完成

[2025-10-23 12:05:46] 🔐 阶段 3/3: 写入 Master Vault...
[2025-10-23 12:05:47] ✅ 已写入 Vault：Master AI 自学习纪要 - 2025-10-23 (Master AI Scheduler) [ID: 42]
[2025-10-23 12:05:47] ✅ Master Vault 写入完成

============================================================
[2025-10-23 12:05:48] 🎉 Master AI 自学习完成！
============================================================
```

### 错误处理日志

```log
[2025-10-23 12:00:00] 🚀 Master AI 自学习启动 | 训练周期: 7 天
[2025-10-23 12:00:01] 📊 阶段 1/3: Evolution Engine - 提炼命盘规律...
[2025-10-23 12:00:02] ❌ Evolution Engine 失败: Database connection error
[2025-10-23 12:00:02] ❌ 自学习过程出错: Database connection error
```

---

## 🧪 测试调度器

### 运行测试脚本

```bash
python test_scheduler.py
```

### 测试输出

```
============================================================
  Master AI Scheduler 系统测试
============================================================

=== 测试 1: AI 规则配置加载 ===
✅ 训练周期: 7 天

=== 测试 2: 日志系统 ===
✅ 日志路径: logs/master_ai_scheduler.log

=== 测试 3: 模块导入 ===
✅ master_ai_evolution_engine 导入成功
✅ master_ai_reasoner 导入成功
✅ master_vault_engine 导入成功
✅ schedule 库导入成功

=== 测试 4: 调度器设置 ===
✅ 调度器配置成功: 每 7 天执行一次

============================================================
🎉 所有测试通过！调度器系统就绪。
============================================================
```

---

## 🔧 高级配置

### 自定义学习范围

编辑 `master_ai_scheduler.py`：

```python
def run_master_self_training():
    # 修改推理用户数量
    reason_all(limit=200)  # 默认 100，可改为 200
```

### 添加自定义步骤

```python
def run_master_self_training():
    # 现有流程...
    
    # 添加自定义步骤
    write_log("\n🔍 阶段 4/4: 自定义分析...")
    try:
        custom_analysis()
        write_log("✅ 自定义分析完成")
    except Exception as e:
        write_log(f"⚠️ 自定义分析失败: {e}")
```

### 修改调度频率

```python
# 每天执行
schedule.every(1).days.do(run_master_self_training)

# 每周执行
schedule.every(7).days.do(run_master_self_training)

# 每月执行（30天）
schedule.every(30).days.do(run_master_self_training)

# 每小时执行（测试用）
schedule.every(1).hours.do(run_master_self_training)
```

---

## 📂 文件结构

```
LynkerAI/
├── master_ai_scheduler.py           # 主调度器
├── test_scheduler.py                # 测试脚本
├── MASTER_AI_SCHEDULER_GUIDE.md     # 使用文档
├── logs/
│   └── master_ai_scheduler.log      # 执行日志
└── master_ai/
    ├── master_ai_evolution_engine.py
    ├── master_ai_reasoner.py
    └── master_vault_engine.py
```

---

## 🔐 安全机制

### 1. **Master Vault 加密**
- 所有学习成果使用 AES256 加密
- 仅 Superintendent Admin 可解密查看
- 完整审计追踪

### 2. **错误隔离**
- 单个阶段失败不影响整体调度
- 非致命错误继续执行
- 详细错误日志记录

### 3. **资源控制**
- 限制 Reasoner 处理用户数（默认100）
- 防止数据库过载
- 优雅的错误恢复

---

## 🛠️ 故障排查

### 问题 1: 调度器无法启动

**可能原因**：
- Supabase 连接失败
- MASTER_VAULT_KEY 未设置
- schedule 库未安装

**解决方法**：
```bash
# 检查环境变量
echo $SUPABASE_URL
echo $MASTER_VAULT_KEY

# 重新安装依赖
uv pip install schedule

# 运行测试
python test_scheduler.py
```

### 问题 2: Evolution Engine 失败

**可能原因**：
- birthcharts 表为空
- 数据格式不正确

**解决方法**：
```sql
-- 检查数据
SELECT COUNT(*) FROM birthcharts;
SELECT * FROM birthcharts LIMIT 5;
```

### 问题 3: Reasoner 超时

**可能原因**：
- 用户数太多
- API 调用频率限制

**解决方法**：
```python
# 减少处理用户数
reason_all(limit=50)  # 从 100 降到 50
```

### 问题 4: 日志文件过大

**解决方法**：
```bash
# 归档旧日志
mv logs/master_ai_scheduler.log logs/master_ai_scheduler_$(date +%Y%m%d).log

# 清空当前日志
> logs/master_ai_scheduler.log
```

---

## 📈 性能优化

### 1. **批量处理**
```python
# 分批推理，避免一次性处理太多用户
for i in range(0, 500, 100):
    reason_all(limit=100, offset=i)
    time.sleep(60)  # 休息1分钟
```

### 2. **并行执行**
```python
from concurrent.futures import ThreadPoolExecutor

def parallel_reasoning():
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(reason_all, limit=25, offset=i*25)
            for i in range(4)
        ]
        results = [f.result() for f in futures]
```

### 3. **缓存优化**
```python
# 缓存规则配置，减少数据库查询
_cached_rules = None
_cache_time = None

def get_cached_rules():
    global _cached_rules, _cache_time
    if not _cached_rules or (time.time() - _cache_time) > 3600:
        _cached_rules = load_ai_rules()
        _cache_time = time.time()
    return _cached_rules
```

---

## 🔄 集成到生产环境

### 使用 systemd（Linux）

创建 `/etc/systemd/system/master-ai-scheduler.service`：

```ini
[Unit]
Description=Master AI Scheduler
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/LynkerAI
ExecStart=/usr/bin/python3 master_ai_scheduler.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl enable master-ai-scheduler
sudo systemctl start master-ai-scheduler
sudo systemctl status master-ai-scheduler
```

### 使用 Docker

```dockerfile
FROM python:3.11

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["python", "master_ai_scheduler.py"]
```

---

## 💡 最佳实践

1. **定期检查日志**
   - 每周查看 `logs/master_ai_scheduler.log`
   - 监控错误和警告信息

2. **合理设置周期**
   - 数据量小：每3天一次
   - 数据量中：每7天一次（推荐）
   - 数据量大：每14天一次

3. **监控资源使用**
   - 观察 CPU 和内存占用
   - 避免高峰期执行

4. **定期备份**
   - 备份 master_vault 表
   - 备份学习日志

---

## 🎯 使用场景

### 场景 1: 全自动运行

```bash
# 启动调度器，完全自动化
python master_ai_scheduler.py
```

### 场景 2: 手动触发单次学习

```python
from master_ai_scheduler import run_master_self_training

# 立即执行一次学习
run_master_self_training()
```

### 场景 3: 自定义调度

```python
import schedule
from master_ai_scheduler import run_master_self_training

# 每天凌晨3点执行
schedule.every().day.at("03:00").do(run_master_self_training)

while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## 📊 监控与分析

### 查看学习历史

```python
from master_vault_engine import list_vault_entries

# 列出所有学习纪要
list_vault_entries()
```

### 分析学习效果

```sql
-- 查看最近的学习纪要
SELECT title, created_by, created_at 
FROM master_vault 
WHERE title LIKE 'Master AI 自学习纪要%'
ORDER BY created_at DESC 
LIMIT 10;
```

---

## ✅ 总结

`master_ai_scheduler.py` 提供了：

✅ **全自动学习** - 无需人工干预  
✅ **灵活配置** - 动态调整训练周期  
✅ **完整日志** - 详细记录执行过程  
✅ **安全加密** - AES256 保护学习成果  
✅ **错误恢复** - 优雅处理异常情况  
✅ **易于集成** - 支持多种部署方式  

---

**文档版本**: 1.0  
**最后更新**: 2025-10-23  
**维护者**: LynkerAI Team
