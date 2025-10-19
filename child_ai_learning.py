"""
child_ai_learning.py
--------------------------------------
📘 功能：
子AI自我成长系统
自动根据用户反馈更新 AI 人格参数：
- 提升 empathy_level（被喜欢多）
- 降低 logic_level（被嫌冷漠多）
- 分析评论关键词，提炼性格方向

--------------------------------------
运行方式：
python child_ai_learning.py
"""

from datetime import datetime
import json, os
import statistics

try:
    from supabase_init import get_supabase
    supabase = get_supabase()
except Exception as e:
    supabase = None
    print(f"⚠️ Supabase连接失败，转为本地模式: {e}")


# ✅ 本地 JSON 备份
def save_local_backup(filename, data):
    os.makedirs("./data", exist_ok=True)
    with open(f"./data/{filename}", "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")
    print(f"💾 本地备份 → {filename}")


# ✅ 获取反馈统计
def fetch_feedback_summary(user_id):
    if not supabase:
        print("⚠️ 无法连接 Supabase，使用本地模式。")
        return None

    resp = supabase.table("child_ai_feedback").select("*").eq("user_id", user_id).execute()
    data = resp.data if resp and resp.data else []
    if not data:
        print("⚠️ 没有反馈记录。")
        return None

    likes = [r for r in data if r["liked"]]
    dislikes = [r for r in data if not r["liked"]]

    print(f"📊 反馈统计：{len(likes)} 👍 | {len(dislikes)} 👎")
    return {
        "total": len(data),
        "likes": len(likes),
        "dislikes": len(dislikes),
        "ratio": len(likes) / len(data) if data else 0
    }


# ✅ 获取并更新人格设定
def update_ai_profile(user_id, feedback_summary):
    if not feedback_summary:
        print("⚠️ 无可更新内容。")
        return

    ratio = feedback_summary["ratio"]

    # ⚙️ 自适应学习逻辑
    empathy_delta = (ratio - 0.5) * 2  # 0.0 ~ ±1.0
    logic_delta = (0.5 - ratio) * 1.5  # 喜欢少则逻辑偏冷

    # 获取现有人格
    profile_resp = supabase.table("child_ai_profiles").select("*").eq("user_id", user_id).execute()
    profile = profile_resp.data[0] if profile_resp.data else {
        "user_id": user_id,
        "personality_type": "普通型",
        "empathy_level": 1.0,
        "logic_level": 1.0,
        "updated_at": datetime.now().isoformat()
    }

    profile["empathy_level"] = round(max(0, profile.get("empathy_level", 1.0) + empathy_delta), 2)
    profile["logic_level"] = round(max(0, profile.get("logic_level", 1.0) + logic_delta), 2)
    profile["updated_at"] = datetime.now().isoformat()

    try:
        supabase.table("child_ai_profiles").upsert(profile).execute()
        print(f"🌿 AI人格已成长 → empathy: {profile['empathy_level']} | logic: {profile['logic_level']}")
    except Exception as e:
        print(f"⚠️ Supabase更新失败，保存至本地。{e}")
        save_local_backup("child_ai_profiles_backup.jsonl", profile)


# ✅ 主运行函数
def run_ai_learning(user_id="u_demo"):
    print(f"🧠 子AI学习启动中：{user_id}")
    summary = fetch_feedback_summary(user_id)
    if summary:
        update_ai_profile(user_id, summary)
    else:
        print("⚠️ 没有有效反馈可学习。")


# ✅ 测试执行
if __name__ == "__main__":
    run_ai_learning("u_demo")
    print("✅ 学习流程完成。")
