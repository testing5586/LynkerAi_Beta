from flask import Flask, request, jsonify
from supabase import create_client
from match_palace import calculate_match_score
import os

app = Flask(__name__)

# 读取 Supabase 凭证
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# AI 解读模板
def generate_ai_comment(matching_fields):
    if "ziwei_palace" in matching_fields and "shen_palace" in matching_fields:
        return "你们的紫微宫与身宫皆同，命格气场共振，容易成为灵魂伴侣或事业拍档。"
    elif "ziwei_palace" in matching_fields:
        return "你们的紫微宫相同，代表人生舞台、格局相似，容易共鸣。"
    elif "shen_palace" in matching_fields:
        return "你们的身宫相同，说明性格节奏与生活方式接近，易产生亲和力。"
    elif "main_star" in matching_fields:
        return "主星相同，思想模式与应变方式类似。"
    else:
        return "气场略有差异，但仍可能互补成长。"

@app.route("/login_refresh", methods=["POST"])
def login_refresh():
    data = request.get_json()
    user_id = data.get("user_id")
    filter_data = data.get("filter", {})

    # 获取登录者的命盘
    user_res = supabase.table("birthcharts").select("*").eq("id", user_id).execute()
    if not user_res.data:
        return jsonify({"error": "User not found"}), 404
    user_chart = user_res.data[0]

    # 获取所有命盘（排除自己）
    query = supabase.table("birthcharts").select("*").neq("id", user_id)

    # 若传入了 filter
    if "couple_palace_star" in filter_data:
        stars = filter_data["couple_palace_star"]
        query = query.in_("main_star", stars)

    all_charts = query.execute().data

    recommendations = []
    for target in all_charts:
        score, fields = calculate_match_score(user_chart, target)
        if score > 0:
            recommendations.append({
                "target_id": target["id"],
                "target_name": target["name"],
                "match_score": score,
                "matching_fields": fields,
                "ai_comment": generate_ai_comment(fields)
            })

    recommendations = sorted(recommendations, key=lambda x: x["match_score"], reverse=True)[:10]

    result = {
        "title": "Top 10 同命推荐榜",
        "user_name": user_chart["name"],
        "user_id": user_chart["id"],
        "recommendations": recommendations
    }

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
