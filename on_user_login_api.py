import os
from flask import Flask, request, jsonify
from supabase import create_client, Client
from match_palace import calculate_match_score

# ===============================
# 初始化
# ===============================
app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ===============================
# 核心函数：生成Top10推荐榜
# ===============================
def generate_recommendations(user_id, match_filter=None):
    charts = supabase.table("birthcharts").select("*").execute().data
    user_chart = next((x for x in charts if x["id"] == user_id), None)

    if not user_chart:
        return {"error": f"未找到用户 {user_id} 的命盘资料。"}

    recommendations = []

    for other in charts:
        if other["id"] == user_id:
            continue

        # 应用自定义筛选条件（例如夫妻宫）
        if match_filter:
            passed = True
            for key, values in match_filter.items():
                if key not in other or str(other[key]) not in values:
                    passed = False
                    break
            if not passed:
                continue

        # 执行匹配计算
        score, fields = calculate_match_score(user_chart, other)
        match_data = {
            "target_id": other["id"],
            "target_name": other["name"],
            "match_score": score,
            "matching_fields": fields,
        }
        recommendations.append(match_data)

    # 排序并取前10
    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    top10 = recommendations[:10]

    return {
        "user_id": user_chart["id"],
        "user_name": user_chart["name"],
        "top10_recommendations": top10
    }


# ===============================
# Flask API 路由
# ===============================
@app.route("/login_refresh", methods=["POST"])
def login_refresh():
    """当用户登入时触发匹配刷新"""
    data = request.get_json()
    user_id = data.get("user_id")
    match_filter = data.get("filter", None)

    if not user_id:
        return jsonify({"error": "缺少参数 user_id"}), 400

    result = generate_recommendations(user_id, match_filter)
    return jsonify(result)


# ===============================
# 启动服务
# ===============================
if __name__ == "__main__":
    import sys
    port = 5000
    if len(sys.argv) > 1 and sys.argv[1] == '--port' and len(sys.argv) > 2:
        port = int(sys.argv[2])
    app.run(host="0.0.0.0", port=port)
