"""
Master–Child–User 三方协作的最小实现：
- JSONL 作为事件总线（简洁可靠）
- /api/relay/send    -> Master 指派任务给 Child（或直接消息）
- /api/relay/callback-> Child 执行完成回传结果
- /api/relay/logs    -> 拉取最近 N 条对话/事件
- /api/relay/ack     -> （可选）对消息进行确认
- 全部写入 conversation_log.jsonl，面向审计与回放
"""
import os, json, time, threading
from typing import Dict, Any, List
from flask import Blueprint, request, jsonify

bp = Blueprint("relay", __name__)
LOG_FILE = "conversation_log.jsonl"
_lock = threading.Lock()

def _append_log(record: Dict[str, Any]):
    record.setdefault("ts", time.strftime("%Y-%m-%d %H:%M:%S"))
    with _lock:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

def _read_logs(limit: int = 100) -> List[Dict[str, Any]]:
    if not os.path.exists(LOG_FILE): return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()[-limit:]
    return [json.loads(x) for x in lines]

@bp.route("/api/relay/send", methods=["POST"])
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

    # 简单自动 task_id
    if data.get("type") == "task" and not data.get("task_id"):
        data["task_id"] = f"t_{int(time.time()*1000)}"

    _append_log({"event":"send", **data})
    return jsonify({"status":"ok", "task_id": data.get("task_id")})

@bp.route("/api/relay/callback", methods=["POST"])
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
    _append_log({"event":"callback", **data})
    return jsonify({"status":"ok"})

@bp.route("/api/relay/logs", methods=["GET"])
def relay_logs():
    limit = int(request.args.get("limit", 100))
    return jsonify({"status":"ok","logs":_read_logs(limit)})

@bp.route("/api/relay/ack", methods=["POST"])
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
