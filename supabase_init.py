from supabase import create_client
import os

def init_supabase():
    """
    初始化 Supabase 连接，并自动检测必需的表。
    检测表：verified_charts, life_event_weights, user_life_tags
    返回 supabase 客户端对象。
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        print("⚠️ Warning: Supabase credentials not found. Results will only be saved locally.")
        return None

    supabase = create_client(url, key)
    print("🔗 Connected to Supabase!")

    # 检测必需的表
    tables_to_check = ["verified_charts", "life_event_weights", "user_life_tags"]
    
    for table_name in tables_to_check:
        try:
            supabase.table(table_name).select("*").limit(1).execute()
            print(f"✅ Table '{table_name}' already exists.")
        except Exception as e:
            print(f"🛠️ Table '{table_name}' not found, it may need to be created manually.")
            print(f"📋 Please create it using the SQL editor in Supabase Dashboard if needed.")

    return supabase
