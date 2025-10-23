"""
Master AI 自动回复器
监听发送给 Master AI 的消息，并使用多模型AI进行智能回复
"""
import os, json, time, requests
from typing import Dict, Any, Optional

LOG_FILE = "conversation_log.jsonl"
STATE_FILE = "master_responder_state.json"
API_KEY = "lynker_relay_secret_2025"
API_BASE = "http://localhost:8008"

def load_state() -> Dict[str, bool]:
    """加载已处理的消息ID"""
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_state(state: Dict[str, bool]):
    """保存已处理的消息ID"""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_pending_messages(processed: Dict[str, bool]) -> list:
    """获取所有未处理的发给Master的消息"""
    if not os.path.exists(LOG_FILE):
        return []
    
    messages = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line)
                if (record.get("event") == "send" and 
                    record.get("to") == "master" and 
                    record.get("type") == "message"):
                    
                    msg_id = f"{record.get('from')}_{record.get('ts')}"
                    if msg_id not in processed:
                        messages.append(record)
            except:
                continue
    return messages

def call_ai(user_message: str) -> Optional[str]:
    """调用多模型AI获取回复"""
    try:
        response = requests.post(
            f"{API_BASE}/api/master-ai/chat",
            json={
                "query": user_message,
                "topk": 5
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("answer", "抱歉，我无法生成回复。")
        else:
            print(f"❌ AI调用失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ AI调用异常: {e}")
        return None

def send_reply(reply_text: str):
    """将Master的回复发送到消息总线"""
    try:
        response = requests.post(
            f"{API_BASE}/api/relay/send",
            headers={
                "Content-Type": "application/json",
                "X-Relay-API-Key": API_KEY
            },
            json={
                "from": "master",
                "to": "user",
                "type": "message",
                "text": reply_text
            },
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 发送回复失败: {e}")
        return False

def process_message(message: Dict[str, Any]) -> bool:
    """处理单个消息"""
    user_text = message.get("text", "")
    print(f"\n📨 收到用户消息: {user_text[:50]}...")
    
    print("🤔 正在思考回复...")
    ai_reply = call_ai(user_text)
    
    if ai_reply:
        print(f"💬 AI回复: {ai_reply[:100]}...")
        success = send_reply(ai_reply)
        if success:
            print("✅ 回复已发送")
            return True
        else:
            print("⚠️ 回复发送失败")
            return False
    else:
        print("⚠️ AI生成失败，跳过此消息")
        return False

def main():
    """主循环"""
    print("🧠 Master AI 自动回复器启动")
    print(f"📂 日志文件: {LOG_FILE}")
    print(f"💾 状态文件: {STATE_FILE}")
    print(f"🔄 开始监听...\n")
    
    state = load_state()
    
    while True:
        try:
            pending = get_pending_messages(state)
            
            if pending:
                print(f"\n📋 发现 {len(pending)} 条待处理消息")
                
                for msg in pending:
                    msg_id = f"{msg.get('from')}_{msg.get('ts')}"
                    
                    success = process_message(msg)
                    
                    if success:
                        state[msg_id] = True
                        save_state(state)
            
            time.sleep(3)
            
        except KeyboardInterrupt:
            print("\n👋 收到退出信号，停止运行")
            break
        except Exception as e:
            print(f"❌ 主循环异常: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
