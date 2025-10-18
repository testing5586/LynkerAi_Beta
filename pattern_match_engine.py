import os
import json
from supabase import create_client, Client
from datetime import datetime
import openai
import math

# ====== CONFIG ======
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
openai.api_key = OPENAI_API_KEY

# ====== 权重设定 ======
WEIGHTS = {
    "ziwei_palace": 0.3,
    "overall_pattern": 0.4,
    "four_transformation_pattern": 0.2,
    "semantic_similarity": 0.1
}

# ====== 获取所有命主资料 ======
def fetch_all_birthcharts():
    data = supabase.table("birthcharts").select("*").execute()
    return data.data

# ====== 基础匹配函数 ======
def basic_match_score(a, b):
    score = 0
    matched_fields = []

    if a["ziwei_palace"] == b["ziwei_palace"]:
        score += WEIGHTS["ziwei_palace"] * 100
        matched_fields.append("ziwei_palace")

    if a.get("overall_pattern") and b.get("overall_pattern") and a["overall_pattern"] == b["overall_pattern"]:
        score += WEIGHTS["overall_pattern"] * 100
        matched_fields.append("overall_pattern")

    if a.get("four_transformation_pattern") and b.get("four_transformation_pattern") and a["four_transformation_pattern"] == b["four_transformation_pattern"]:
        score += WEIGHTS["four_transformation_pattern"] * 100
        matched_fields.append("four_transformation_pattern")

    return score, matched_fields

# ====== 语义相似度（AI计算） ======
def semantic_similarity(a_summary, b_summary):
    try:
        emb_a = openai.embeddings.create(model="text-embedding-3-small", input=a_summary)["data"][0]["embedding"]
        emb_b = openai.embeddings.create(model="text-embedding-3-small", input=b_summary)["data"][0]["embedding"]

        dot = sum(x*y for x, y in zip(emb_a, emb_b))
        norm_a = math.sqrt(sum(x**2 for x in emb_a))
        norm_b = math.sqrt(sum(x**2 for x in emb_b))
        return (dot / (norm_a * norm_b)) * 100  # 转换为 0–100
    except Exception:
        return 0

# ====== AI 生成断语 ======
def generate_ai_comment(user_name, target_name, matched_fields):
    fields_text = "、".join(matched_fields)
    prompt = f"以紫微斗数命理师的口吻写一句人性化分析：{user_name} 与 {target_name} 的命盘相似之处在 {fields_text}，请给出简短评论。"
    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=80
    )
    return resp.choices[0].message.content.strip()

# ====== 主函数 ======
def find_top_matches(user_id):
    charts = fetch_all_birthcharts()
    user = next((c for c in charts if c["id"] == user_id), None)
    if not user:
        return {"error": "User not found"}

    recommendations = []

    for target in charts:
        if target["id"] == user_id:
            continue

        score, matched = basic_match_score(user, target)

        if user.get("life_summary") and target.get("life_summary"):
            semantic_score = semantic_similarity(user["life_summary"], target["life_summary"])
            score += WEIGHTS["semantic_similarity"] * semantic_score
        else:
            semantic_score = 0

        ai_comment = generate_ai_comment(user["name"], target["name"], matched)

        recommendations.append({
            "target_id": target["id"],
            "target_name": target["name"],
            "match_score": round(score, 2),
            "matching_fields": matched,
            "ai_comment": ai_comment
        })

    recommendations = sorted(recommendations, key=lambda x: x["match_score"], reverse=True)[:10]

    return {
        "title": "Top 10 同格局推荐榜",
        "user_id": user_id,
        "user_name": user["name"],
        "recommendations": recommendations
    }

if __name__ == "__main__":
    result = find_top_matches(2)
    print(json.dumps(result, ensure_ascii=False, indent=2))
