import os
import datetime
from supabase import create_client, Client
from ai_truechart_verifier import verify_chart

# === 环境变量读取 ===
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === 用户 AI 调用配额配置 ===
DAILY_LIMIT_DEFAULT = 50

def get_user(user_id):
    """获取用户资料"""
    resp = supabase.table("users").select("*").eq("id", user_id).execute()
    if not resp.data:
        return None
    return resp.data[0]

def get_ai_rules():
    """从 ai_rules 表读取所有控制规则"""
    resp = supabase.table("ai_rules").select("*").execute()
    rules = {r["rule_name"]: r["rule_value"] for r in resp.data}
    return rules

def get_today_usage(user_id):
    """获取用户今日调用次数"""
    today = datetime.date.today().isoformat()
    resp = supabase.table("ai_usage_log").select("*").eq("user_id", user_id).eq("date", today).execute()
    if not resp.data:
        return 0
    return resp.data[0].get("count", 0)

def update_usage(user_id):
    """更新用户今日调用次数"""
    today = datetime.date.today().isoformat()
    usage = get_today_usage(user_id)
    if usage == 0:
        supabase.table("ai_usage_log").insert({
            "user_id": user_id,
            "date": today,
            "count": 1
        }).execute()
    else:
        supabase.table("ai_usage_log").update({
            "count": usage + 1
        }).eq("user_id", user_id).eq("date", today).execute()

def check_ai_permission(user_id):
    """判断用户是否还能调用 AI"""
    # 第一步：命盘验证检查
    result = verify_chart(user_id)
    if result["status"] == "verified":
        verification_msg = f"命盘已验证，置信度：{result['confidence']}"
    else:
        return {"status": "need_verification", "msg": "请先完成真命盘验证"}

    user = get_user(user_id)
    if not user:
        return {"status": "error", "msg": "用户不存在"}

    rules = get_ai_rules()
    role = user.get("role", "user")
    provider = user.get("ai_provider", "mock-ai")

    # Lynker Master 永远不受限
    if role == "admin":
        return {"status": "ok", "msg": f"Lynker Master 权限无限制 ({verification_msg})"}

    # 检查是否被主AI停用
    if user.get("ai_status") == "disabled":
        return {"status": "blocked", "msg": "AI助手已被停用，请联系 Lynker Master"}

    # 检查每日配额
    usage = get_today_usage(user_id)
    limit = int(rules.get("daily_limit", DAILY_LIMIT_DEFAULT))
    if usage >= limit:
        supabase.table("users").update({"ai_status": "disabled"}).eq("id", user_id).execute()
        return {"status": "blocked", "msg": f"已达到每日调用上限 ({limit}次)，AI助手自动停用"}

    # 正常通过
    update_usage(user_id)
    return {"status": "ok", "msg": f"允许调用 ({usage+1}/{limit})，{verification_msg}"}

def master_control(action, target_user_id):
    """Lynker Master 远程控制接口"""
    if action == "enable":
        supabase.table("users").update({"ai_status": "active"}).eq("id", target_user_id).execute()
        return f"✅ 已启用用户 {target_user_id} 的 AI 助手"
    elif action == "disable":
        supabase.table("users").update({"ai_status": "disabled"}).eq("id", target_user_id).execute()
        return f"🛑 已停用用户 {target_user_id} 的 AI 助手"
    else:
        return "未知指令"

# === 演示运行 ===
if __name__ == "__main__":
    print("🚀 LynkerAI 主控规则引擎启动中...\n")

    user_id = 2  # 例：命主A
    result = check_ai_permission(user_id)
    print(result)

    # 管理员命令示例：
    # print(master_control("disable", 2))
    # print(master_control("enable", 2))
