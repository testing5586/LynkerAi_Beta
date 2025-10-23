import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def load_ai_rules():
    """从 ai_rules 表中读取模型配置"""
    if not client:
        print("⚠️ Supabase 客户端未初始化，使用默认配置")
        return {
            "MODEL_FREE": "gpt-4o-mini",
            "MODEL_PRO": "gpt-4-turbo",
            "MODEL_MASTER": "gpt-4-turbo",
            "TRAINING_INTERVAL_DAYS": 7
        }
    
    try:
        resp = client.table("ai_rules").select("*").execute()
        if not resp.data:
            return {
                "MODEL_FREE": "gpt-4o-mini",
                "MODEL_PRO": "gpt-4-turbo",
                "MODEL_MASTER": "gpt-4-turbo",
                "TRAINING_INTERVAL_DAYS": 7
            }
        
        data = {}
        for r in resp.data:
            if isinstance(r, dict):
                rule_name = r.get("rule_name")
                rule_value = r.get("rule_value")
                if rule_name and rule_value:
                    data[rule_name] = rule_value
        
        return {
            "MODEL_FREE": data.get("MODEL_FREE", "gpt-4o-mini"),
            "MODEL_PRO": data.get("MODEL_PRO", "gpt-4-turbo"),
            "MODEL_MASTER": data.get("MODEL_MASTER", "gpt-4-turbo"),
            "TRAINING_INTERVAL_DAYS": int(data.get("TRAINING_INTERVAL_DAYS", "7"))
        }
    except Exception as e:
        print(f"⚠️ 无法加载 AI 规则: {e}")
        return {
            "MODEL_FREE": "gpt-4o-mini",
            "MODEL_PRO": "gpt-4-turbo",
            "MODEL_MASTER": "gpt-4-turbo",
            "TRAINING_INTERVAL_DAYS": 7
        }

def get_model_for_user(user_id: int):
    """
    根据用户身份选择 AI 模型
    
    参数:
        user_id: 用户 ID
    
    返回:
        模型名称（如 "gpt-4o-mini", "gpt-4-turbo" 等）
    
    规则:
        - Superintendent Admin → MODEL_MASTER
        - Pro 用户 → MODEL_PRO
        - 普通用户 → MODEL_FREE
    """
    if not client:
        print("⚠️ Supabase 客户端未初始化，使用默认模型")
        return "gpt-4o-mini"
    
    try:
        user = client.table("users").select("role, ai_provider").eq("id", user_id).execute()
        if not user.data or len(user.data) == 0:
            print(f"⚠️ 未找到用户 ID {user_id}，使用默认模型")
            return "gpt-4o-mini"
        
        user_record = user.data[0]
        if not isinstance(user_record, dict):
            return "gpt-4o-mini"
        
        role = user_record.get("role", "user")
        provider = user_record.get("ai_provider", "free")

        rules = load_ai_rules()

        if role == "Superintendent Admin":
            model = rules["MODEL_MASTER"]
            print(f"👑 用户 {user_id} (Superintendent Admin) → 使用 {model}")
            return model
        elif provider == "pro":
            model = rules["MODEL_PRO"]
            print(f"💎 用户 {user_id} (Pro) → 使用 {model}")
            return model
        else:
            model = rules["MODEL_FREE"]
            print(f"🆓 用户 {user_id} (Free) → 使用 {model}")
            return model
            
    except Exception as e:
        print(f"⚠️ 获取模型失败: {e}")
        return "gpt-4o-mini"

def get_api_key_for_user(user_id: int):
    """
    根据用户身份选择 API Key
    
    参数:
        user_id: 用户 ID
    
    返回:
        OpenAI API Key
    
    规则:
        - Superintendent Admin / Master AI → LYNKER_MASTER_KEY
        - 普通用户 → OPENAI_API_KEY (用户自己的)
    """
    if not client:
        return os.getenv("OPENAI_API_KEY")
    
    try:
        user = client.table("users").select("role").eq("id", user_id).execute()
        if not user.data or len(user.data) == 0:
            return os.getenv("OPENAI_API_KEY")
        
        user_record = user.data[0]
        if not isinstance(user_record, dict):
            return os.getenv("OPENAI_API_KEY")
        
        role = user_record.get("role", "user")
        
        if role == "Superintendent Admin":
            master_key = os.getenv("LYNKER_MASTER_KEY")
            if master_key:
                print(f"🔑 使用 Lynker Master Key (用户 {user_id})")
                return master_key
        
        return os.getenv("OPENAI_API_KEY")
        
    except Exception as e:
        print(f"⚠️ 获取 API Key 失败: {e}")
        return os.getenv("OPENAI_API_KEY")

if __name__ == "__main__":
    print("=== Multi-Model Dispatcher 测试 ===\n")
    
    print("📋 AI 规则配置:")
    rules = load_ai_rules()
    for key, value in rules.items():
        print(f"  {key}: {value}")
    
    print("\n🧪 测试用户模型选择:")
    test_user_ids = [1, 2, 3, 4, 5]
    for uid in test_user_ids:
        model = get_model_for_user(uid)
        print(f"  用户 {uid} → {model}")
