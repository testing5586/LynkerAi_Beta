# Conversation Bus - 消息中枢系统

## 概述
Master-Child-User 三方协作的消息总线系统，支持任务分派、异步回调、对话追踪。

## 核心特性

### ✅ 已实现功能
1. **API Key 认证**：保护所有写操作端点，防止未授权访问
2. **任务状态追踪**：持久化任务状态（pending → completed/failed）
3. **可靠回调**：Child worker 仅在回调成功后标记任务完成
4. **防重复执行**：Worker 状态持久化，重启后不会重复处理
5. **自动重试**：回调失败时自动重试（最多 3 次，指数退避）
6. **线程安全**：单进程内的并发请求安全

### 🔧 API 端点

#### POST /api/relay/send
发送任务/消息（需要认证）

**请求头**：
```
X-Relay-API-Key: lynker_relay_secret_2025
```

**请求体**：
```json
{
  "from": "master",
  "to": "child",
  "type": "task",
  "cmd": "verify_chart",
  "payload": {"user_id": "u123"},
  "text": "请验证此命盘"
}
```

**响应**：
```json
{
  "status": "ok",
  "task_id": "t_1761141014541"
}
```

#### POST /api/relay/callback
Child AI 任务回调（需要认证）

**请求体**：
```json
{
  "task_id": "t_1761141014541",
  "child_id": "child_bazi",
  "status": "done",
  "result": {"summary": "命盘验证完成", "score": 0.85}
}
```

#### GET /api/relay/logs?limit=50
查询对话日志（无需认证）

#### GET /api/relay/task-status/<task_id>
查询任务状态（无需认证）

**响应**：
```json
{
  "status": "ok",
  "task_id": "t_1761141014541",
  "task_status": "completed"
}
```

## 部署要求

### ⚠️ 重要限制

**当前实现适用于单进程部署**（如 `python app.py` 或单 worker Gunicorn）。

如果需要多进程部署（如 `gunicorn -w 4`），需要升级并发控制机制：

1. **问题**：`threading.Lock` 仅保护单进程内的线程，多进程写入会产生竞态条件
2. **解决方案**：
   - 使用文件锁（`fcntl.flock`）
   - 使用 SQLite 存储任务状态
   - 使用 Redis 作为状态存储
   - 使用 PostgreSQL 表替代 JSON 文件

### 推荐部署配置

**Replit 环境（默认）**：
```bash
python master_ai_uploader_api.py  # 单进程，安全
```

**生产环境（单 worker）**：
```bash
gunicorn -w 1 -b 0.0.0.0:8008 master_ai_uploader_api:app
```

**生产环境（多 worker - 需要升级）**：
- 先实现跨进程锁机制
- 或使用数据库存储任务状态

## Child Worker 使用

### 启动 Worker
```bash
export LYNKER_API_BASE=http://your-api-domain:8008
export RELAY_API_KEY=lynker_relay_secret_2025
python child_worker_mock.py
```

### Worker 特性
- ✅ 持久化状态防重复
- ✅ 回调失败自动重试
- ✅ 详细日志输出
- ✅ 安全认证

## 文件说明

- **conversation_log.jsonl**：事件审计日志（不可变，仅追加）
- **task_state.json**：任务状态存储（Master 维护）
- **child_worker_state.json**：Worker 处理状态（Child 维护）

## 安全建议

1. **生产环境**：修改默认 API Key
   ```bash
   export RELAY_API_KEY=your_secure_random_key
   ```

2. **HTTPS**：生产环境启用 HTTPS 保护 API Key 传输

3. **访问控制**：根据需要添加用户级权限验证

## 性能优化建议

1. **日志轮转**：定期归档 `conversation_log.jsonl`
2. **状态清理**：定期清理旧任务状态
3. **数据库升级**：高并发场景使用 PostgreSQL 替代 JSON 文件

## 测试

### 基础测试
```bash
# 发送任务
curl -X POST http://localhost:8008/api/relay/send \
  -H "X-Relay-API-Key: lynker_relay_secret_2025" \
  -H "Content-Type: application/json" \
  -d '{"from":"master","to":"child","type":"task","cmd":"test"}'

# 查询状态
curl http://localhost:8008/api/relay/task-status/<task_id>

# 查询日志
curl http://localhost:8008/api/relay/logs?limit=10
```

### 并发测试（单进程安全）
```bash
for i in {1..10}; do
  curl -X POST http://localhost:8008/api/relay/send \
    -H "X-Relay-API-Key: lynker_relay_secret_2025" \
    -d "{\"from\":\"master\",\"to\":\"child\",\"type\":\"task\",\"cmd\":\"test_$i\"}" &
done
wait
```

## 架构演进路径

### Phase 1: MVP（当前）
- ✅ JSONL 事件日志
- ✅ JSON 文件状态存储
- ✅ 单进程线程安全
- ✅ API Key 认证

### Phase 2: 生产强化（未来）
- ⏳ PostgreSQL 状态存储
- ⏳ 跨进程文件锁 / Redis
- ⏳ 用户级权限系统
- ⏳ 任务优先级队列

### Phase 3: 分布式（可选）
- ⏳ 消息队列（RabbitMQ/Kafka）
- ⏳ 分布式事务
- ⏳ 横向扩展支持

## 许可证
MIT
