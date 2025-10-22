"""
Child AI 伪执行器（本地模拟）：
- 拉取 conversation_log.jsonl 里的 task 事件（to=child）
- 根据 cmd 简单处理后，向 /api/relay/callback 回传结果
实际部署时，你可以把这个文件独立运行在子 AI 的容器/函数里。
"""
import json, time, os, requests

API_BASE = os.getenv("LYNKER_API_BASE", "http://127.0.0.1:8008")
LOG_FILE = "conversation_log.jsonl"
SEEN = set()

def iter_tasks():
    if not os.path.exists(LOG_FILE): return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
                if r.get("event")=="send" and r.get("to")=="child" and r.get("type")=="task":
                    yield r
            except: 
                continue

def handle_task(task):
    cmd = task.get("cmd")
    payload = task.get("payload", {})
    if cmd == "verify_chart":
        result = {"summary":"已根据 Vault 规则初检命盘轨迹一致性","score":0.72}
    elif cmd == "generate_brief":
        result = {"brief": f"根据资料，{payload.get('topic','主题')} 初步要点已生成。"}
    else:
        result = {"echo": payload}
    return result

def main():
    print("🧒 Child Worker mock running...")
    while True:
        for t in iter_tasks():
            tid = t.get("task_id")
            if tid in SEEN: 
                continue
            SEEN.add(tid)
            res = handle_task(t)
            requests.post(f"{API_BASE}/api/relay/callback", json={
                "task_id": tid,
                "child_id": "child_bazi",
                "status": "done",
                "result": res
            })
        time.sleep(2)

if __name__ == "__main__":
    main()
