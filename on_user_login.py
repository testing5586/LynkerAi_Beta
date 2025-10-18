import os
from supabase import create_client, Client
from match_palace import calculate_match_score

# ===============================
# 环境变量
# ===============================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ===============================
# 登入触发匹配
# ===============================
def refresh_match_for_user(user_id, match_filter=None):
    """
    当用户登入 LynkerAi 时自动执行命盘匹配并生成 Top 10 推荐榜
    match_filter: dict，可选条件，如 {"couple_palace_star": ["廉贞", "破军"]}
    """
    print(f"🔔 用户 {user_id} 登入，开始刷新同命匹配...")

    # 获取所有命盘资料
    charts = supabase.table("birthcharts").select("*").execute().data
    user_chart = next((x for x in charts if x["id"] == user_id), None)

    if not user_chart:
        print(f"⚠️ 未找到用户 {user_id} 的命盘资料。")
        return

    recommendations = []

    for other in charts:
        if other["id"] == user_id:
            continue

        # --- 应用自定义筛选条件 ---
        if match_filter:
            for key, values in match_filter.items():
                if key not in other or str(other[key]) not in values:
                    # 如果条件不符合，跳过此人
                    continue

        # --- 执行匹配计算 ---
        score, fields = calculate_match_score(user_chart, other)
        match_data = {
            "user_a_id": user_chart["id"],
            "user_a_name": user_chart["name"],
            "user_b_id": other["id"],
            "user_b_name": other["name"],
            "match_score": score,
            "matching_fields": ", ".join(fields),
        }

        supabase.table("match_results").upsert(match_data).execute()
        recommendations.append(match_data)

    # --- 排序并取前10 ---
    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    top10 = recommendations[:10]

    print("\n🎯 用户登入后的 Top 10 同命推荐榜：")
    for i, rec in enumerate(top10, 1):
        print(f"{i}. {rec['user_b_name']} - {rec['match_score']} 分 ({rec['matching_fields']})")

    print("\n✅ 同命推荐榜生成完毕。")

# ===============================
# 模拟登入测试
# ===============================
if __name__ == "__main__":
    # 假设用户ID=2登入
    # 模拟：想找夫妻宫含廉贞、破军的人
    filter_condition = {
        "couple_palace_star": ["廉贞", "破军"]
    }

    refresh_match_for_user(user_id=2, match_filter=filter_condition)
