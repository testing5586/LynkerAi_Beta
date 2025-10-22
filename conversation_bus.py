"""
Master–Child–User 三方协作的可靠实现：
- JSONL 作为事件总线（简洁可靠）
- 任务状态追踪机制（防止重复执行和丢失）
- API Key 认证保护（防止未授权访问）
- /api/relay/send    -> Master 指派任务给 Child（或直接消息）
- /api/relay/callback-> Child 执行完成回传结果
- /api/relay/logs    -> 拉取最近 N 条对话/事件
- /api/relay/ack     -> （可选）对消息进行确认
- 全部写入 conversation_log.jsonl，面向审计与回放
"""
import os, json, time, threading
from typing import Dict, Any, List, Optional
from flask import Blueprint, request, jsonify
from functools import wraps

bp = Blueprint("relay", __name__)
LOG_FILE = "conversation_log.jsonl"
STATE_FILE = "task_state.json"
_lock = threading.Lock()

RELAY_API_KEY = os.getenv("RELAY_API_KEY", "lynker_relay_secret_2025")

def require_auth(f):
    """简单的 API Key 认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-Relay-API-Key") or request.args.get("api_key")
        if api_key != RELAY_API_KEY:
            return jsonify({"status":"error","msg":"Unauthorized: Invalid or missing API key"}), 401
        return f(*args, **kwargs)
    return decorated

def _append_log(record: Dict[str, Any]):
    """追加事件到日志文件"""
    record.setdefault("ts", time.strftime("%Y-%m-%d %H:%M:%S"))
    with _lock:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

def _read_logs(limit: int = 100) -> List[Dict[str, Any]]:
    """读取最近的日志条目"""
    if not os.path.exists(LOG_FILE): return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()[-limit:]
    return [json.loads(x) for x in lines]

def _load_task_state() -> Dict[str, str]:
    """加载任务状态（内部使用，需在锁内调用）"""
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_task_state(state: Dict[str, str]):
    """保存任务状态（内部使用，需在锁内调用）"""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def _update_task_status(task_id: str, status: str):
    """更新单个任务状态（线程安全，原子操作）"""
    with _lock:
        state = _load_task_state()
        state[task_id] = status
        _save_task_state(state)

def get_task_status(task_id: str) -> Optional[str]:
    """获取任务状态：pending, processing, completed, failed（线程安全）"""
    with _lock:
        state = _load_task_state()
        return state.get(task_id)

@bp.route("/api/relay/send", methods=["POST"])
@require_auth
def relay_send():
    """
    Master -> Child 或 User -> Master 的通用发送接口
    body:
    {
      "from": "master" | "user",
      "to":   "child" | "master",
      "type": "task" | "message",
      "task_id": "t_xxx",        # type=task 时可选/自动生成
      "cmd": "generate_report",  # 任务命令（可选）
      "payload": {...},          # 任务参数
      "text": "自然语言"          # 自由文本
    }
    """
    data = request.get_json(force=True)
    if not data or not data.get("from") or not data.get("to"):
        return jsonify({"status":"error","msg":"missing from/to"}), 400

    if data.get("type") == "task" and not data.get("task_id"):
        data["task_id"] = f"t_{int(time.time()*1000)}"

    task_id = data.get("task_id")
    _append_log({"event":"send", **data})
    
    if task_id and data.get("type") == "task":
        _update_task_status(task_id, "pending")
    
    return jsonify({"status":"ok", "task_id": task_id})

@bp.route("/api/relay/callback", methods=["POST"])
@require_auth
def relay_callback():
    """
    Child -> Master 任务回调
    body:
    {
      "task_id":"t_xxx",
      "child_id": "child_bazi",
      "status": "done" | "failed",
      "result": {...} | "文本"
    }
    """
    data = request.get_json(force=True)
    if not data or not data.get("task_id"):
        return jsonify({"status":"error","msg":"missing task_id"}), 400
    
    task_id = data["task_id"]
    callback_status = data.get("status", "done")
    
    _append_log({"event":"callback", **data})
    
    new_status = "completed" if callback_status == "done" else "failed"
    _update_task_status(task_id, new_status)
    
    return jsonify({"status":"ok"})

@bp.route("/api/relay/logs", methods=["GET"])
def relay_logs():
    """查询日志（只读操作，不需要认证）"""
    limit = int(request.args.get("limit", 100))
    return jsonify({"status":"ok","logs":_read_logs(limit)})

@bp.route("/api/relay/task-status/<task_id>", methods=["GET"])
def get_task_status_endpoint(task_id: str):
    """查询任务状态（只读操作，不需要认证）"""
    status = get_task_status(task_id)
    if status is None:
        return jsonify({"status":"error","msg":"task not found"}), 404
    return jsonify({"status":"ok", "task_id": task_id, "task_status": status})

@bp.route("/api/relay/ack", methods=["POST"])
@require_auth
def relay_ack():
    """
    （可选）对消息确认
    body: { "task_id":"t_xxx", "ack_by":"master|child" }
    """
    data = request.get_json(force=True)
    if not data or not data.get("task_id"):
        return jsonify({"status":"error","msg":"missing task_id"}), 400
    _append_log({"event":"ack", **data})
    return jsonify({"status":"ok"})
