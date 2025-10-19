from supabase import create_client
import os

def init_supabase():
    """
    初始化 Supabase 连接，并自动检测或创建 verified_charts 表。
    返回 supabase 客户端对象。
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        print("⚠️ Warning: Supabase credentials not found. Results will only be saved locally.")
        return None

    supabase = create_client(url, key)
    print("🔗 Connected to Supabase!")

    try:
        # 尝试查询表，检查是否存在
        supabase.table("verified_charts").select("id").limit(1).execute()
        print("✅ Table 'verified_charts' already exists.")
    except Exception as e:
        print("🛠️ Table 'verified_charts' not found, it may need to be created manually.")
        print("📋 Please create it using the SQL editor in Supabase Dashboard if needed.")

    return supabase
