import os
from datetime import date
from supabase import create_client, Client
from postgrest.exceptions import APIError

# 初始化 Supabase 客户端
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def check_permission(user_id: int):
    """
    LynkerAI 调用前守卫：检查用户是否可调用 AI。
    """

    # Step 1: 读取规则
    try:
        rule_data = supabase.table("ai_rules").select("*").eq("active", True).execute()
        rules = {r["rule_name"]: r.get("rule_value", "True") for r in rule_data.data}
    except Exception as e:
        print(f"⚠️ 无法读取规则: {e}")
        return {"status": "error", "msg": "规则读取失败"}

    # Step 2: 检查是否全局停用
    if rules.get("global_pause", "false").lower() == "true":
        return {"status": "blocked", "msg": "Lynker Master 暂停了所有 AI 调用"}

    # Step 3: 获取用户信息
    try:
        user_resp = supabase.table("users").select("*").eq("id", user_id).execute()
        if not user_resp.data:
            return {"status": "error", "msg": "用户不存在"}
        user = user_resp.data[0]
    except APIError as e:
        return {"status": "error", "msg": f"数据库错误: {e}"}

    # Step 4: 检查是否被禁用
    if user.get("ai_provider") == "banned":
        return {"status": "blocked", "msg": "用户已被禁用"}

    # Step 5: 检查调用上限
    today = str(date.today())
    usage_resp = supabase.table("ai_usage_log").select("*").eq("user_id", user_id).eq("date", today).execute()
    count = usage_resp.data[0]["count"] if usage_resp.data else 0

    limit = int(rules.get("daily_limit", 50))
    if count >= limit:
        return {"status": "blocked", "msg": f"已达到每日上限 ({count}/{limit})"}

    # Step 6: 写入调用日志
    if usage_resp.data:
        supabase.table("ai_usage_log").update({"count": count + 1}).eq("user_id", user_id).eq("date", today).execute()
    else:
        supabase.table("ai_usage_log").insert({"user_id": user_id, "date": today, "count": 1}).execute()

    return {"status": "ok", "msg": f"允许调用 ({count + 1}/{limit})"}


# 示例测试
if __name__ == "__main__":
    print("🚀 LynkerAI 守卫系统测试中...\n")
    result = check_permission(user_id=2)
    print(result)
