import os
import openai
from supabase import create_client, Client

def check_env_vars():
    print("🔍 Checking Environment Variables...\n")

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    results = []

    if supabase_url and "supabase.co" in supabase_url:
        results.append("✅ SUPABASE_URL found and looks valid")
    else:
        results.append("❌ SUPABASE_URL missing or invalid")

    if supabase_key and len(supabase_key) > 30:
        results.append("✅ SUPABASE_KEY found")
    else:
        results.append("❌ SUPABASE_KEY missing or invalid")

    if openai_key and openai_key.startswith("sk-"):
        results.append("✅ OPENAI_API_KEY found")
    else:
        results.append("❌ OPENAI_API_KEY missing or invalid")

    print("\n".join(results))
    print("\n--------------------------------------------------")

    # Test Supabase connection
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        res = supabase.table("birthcharts").select("id, name").limit(1).execute()
        print(f"🧠 Supabase connection OK — {len(res.data)} record(s) retrieved.")
    except Exception as e:
        print(f"⚠️ Supabase connection failed: {e}")

    print("--------------------------------------------------")

    # Test OpenAI connection
    try:
        openai.api_key = openai_key
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "LynkerAI 环境测试"}],
            max_tokens=10
        )
        print(f"🤖 OpenAI connection OK — Model replied: {response.choices[0].message.content.strip()}")
    except Exception as e:
        print(f"⚠️ OpenAI connection failed: {e}")

    print("--------------------------------------------------")
    print("✅ Environment check complete.")

if __name__ == "__main__":
    check_env_vars()
