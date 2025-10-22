"""
Child AI 可靠执行器（改进版）：
- 拉取 conversation_log.jsonl 里的 task 事件（to=child）
- 根据 cmd 简单处理后，向 /api/relay/callback 回传结果
- 持久化任务状态，防止重复执行和结果丢失
- 回调失败时自动重试，确保结果不丢失
实际部署时，你可以把这个文件独立运行在子 AI 的容器/函数里。
"""
import json, time, os, requests

API_BASE = os.getenv("LYNKER_API_BASE", "http://127.0.0.1:8008")
RELAY_API_KEY = os.getenv("RELAY_API_KEY", "lynker_relay_secret_2025")
LOG_FILE = "conversation_log.jsonl"
WORKER_STATE_FILE = "child_worker_state.json"
MAX_RETRIES = 3

def load_worker_state():
    """加载 worker 处理状态（持久化）"""
    if not os.path.exists(WORKER_STATE_FILE):
        return {}
    with open(WORKER_STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_worker_state(state):
    """保存 worker 状态"""
    with open(WORKER_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def mark_task_processed(task_id):
    """标记任务为已处理（仅在回调成功后调用）"""
    state = load_worker_state()
    state[task_id] = {"status": "processed", "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
    save_worker_state(state)

def is_task_processed(task_id):
    """检查任务是否已处理"""
    state = load_worker_state()
    return task_id in state

def iter_tasks():
    """迭代所有待处理的任务"""
    if not os.path.exists(LOG_FILE): 
        return []
    tasks = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
                if r.get("event")=="send" and r.get("to")=="child" and r.get("type")=="task":
                    task_id = r.get("task_id")
                    if task_id and not is_task_processed(task_id):
                        tasks.append(r)
            except: 
                continue
    return tasks

def handle_task(task):
    """处理任务逻辑"""
    cmd = task.get("cmd")
    payload = task.get("payload", {})
    if cmd == "verify_chart":
        result = {"summary":"已根据 Vault 规则初检命盘轨迹一致性","score":0.72}
    elif cmd == "generate_brief":
        result = {"brief": f"根据资料，{payload.get('topic','主题')} 初步要点已生成。"}
    else:
        result = {"echo": payload}
    return result

def send_callback_with_retry(task_id, child_id, status, result):
    """发送回调，失败时重试"""
    callback_data = {
        "task_id": task_id,
        "child_id": child_id,
        "status": status,
        "result": result
    }
    
    headers = {"X-Relay-API-Key": RELAY_API_KEY}
    
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(
                f"{API_BASE}/api/relay/callback",
                json=callback_data,
                headers=headers,
                timeout=10
            )
            if resp.status_code == 200:
                print(f"✅ 回调成功: {task_id}")
                return True
            else:
                print(f"⚠️ 回调失败 (状态码 {resp.status_code}), 重试 {attempt+1}/{MAX_RETRIES}")
        except Exception as e:
            print(f"⚠️ 回调异常: {e}, 重试 {attempt+1}/{MAX_RETRIES}")
        
        if attempt < MAX_RETRIES - 1:
            time.sleep(2 ** attempt)
    
    print(f"❌ 回调最终失败: {task_id}")
    return False

def main():
    print("🧒 Child Worker (可靠版) running...")
    print(f"📍 API Base: {API_BASE}")
    print(f"🔐 Using API Key: {RELAY_API_KEY[:10]}...")
    
    while True:
        tasks = iter_tasks()
        if tasks:
            print(f"📋 发现 {len(tasks)} 个待处理任务")
        
        for task in tasks:
            tid = task.get("task_id")
            print(f"🔄 处理任务: {tid} (cmd={task.get('cmd')})")
            
            result = handle_task(task)
            
            success = send_callback_with_retry(
                task_id=tid,
                child_id="child_bazi",
                status="done",
                result=result
            )
            
            if success:
                mark_task_processed(tid)
                print(f"✅ 任务完成并标记: {tid}")
            else:
                print(f"⚠️ 任务未标记，将在下次重试: {tid}")
        
        time.sleep(2)

if __name__ == "__main__":
    main()
