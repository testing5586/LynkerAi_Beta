import os
import json
import math
from datetime import datetime
from supabase import create_client, Client
import openai
from ai_guard_middleware import check_permission

# ====== 从环境变量读取主密钥 ======
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
MASTER_OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# 初始化 Supabase 客户端
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ====== 权重设定 ======
WEIGHTS = {
    "ziwei_palace": 0.3,
    "overall_pattern": 0.4,
    "four_transformation_pattern": 0.2,
    "semantic_similarity": 0.1
}

# ====== 获取用户专属 AI Key ======
def get_user_ai_key(user_id):
    try:
        res = supabase.table("users").select("ai_api_key").eq("id", user_id).execute()
        if res.data and res.data[0].get("ai_api_key"):
            print(f"🔑 使用命主 {user_id} 的自有 AI 助手 Key")
            return res.data[0]["ai_api_key"]
    except Exception as e:
        print(f"⚠️ 无法读取用户 AI Key: {e}")
    print("🧠 使用 LynkerAI 平台主 Key")
    return MASTER_OPENAI_KEY

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

# ====== 语义相似度计算 ======
def semantic_similarity(a_summary, b_summary, openai_key):
    try:
        openai.api_key = openai_key
        emb_a = openai.embeddings.create(model="text-embedding-3-small", input=a_summary)["data"][0]["embedding"]
        emb_b = openai.embeddings.create(model="text-embedding-3-small", input=b_summary)["data"][0]["embedding"]

        dot = sum(x * y for x, y in zip(emb_a, emb_b))
        norm_a = math.sqrt(sum(x ** 2 for x in emb_a))
        norm_b = math.sqrt(sum(x ** 2 for x in emb_b))
        return (dot / (norm_a * norm_b)) * 100
    except Exception as e:
        print(f"❌ 语义相似度计算失败: {e}")
        return 0

# ====== AI 命理评论 ======
def generate_ai_comment(user_name, target_name, matched_fields, openai_key):
    openai.api_key = openai_key
    if not matched_fields:
        return f"{user_name} 与 {target_name} 命格差异较大，互补而非相同。"
    fields_text = "、".join(matched_fields)
    prompt = f"以紫微斗数命理师的口吻写一句简短分析：{user_name} 与 {target_name} 的命盘相似之处在 {fields_text}，请给出一句命理断语。"
    try:
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ AI 评论生成失败: {e}")
        return f"{user_name} 与 {target_name} 的命格部分相似。"

# ====== 检查并创建 recommendations 表 ======
def ensure_recommendations_table():
    try:
        supabase.table("recommendations").select("id").limit(1).execute()
        return
    except Exception:
        print("🛠️ Creating recommendations table...")
        supabase.rpc(
            "exec",
            {
                "sql": """
                CREATE TABLE IF NOT EXISTS recommendations (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER,
                    target_id INTEGER,
                    match_score FLOAT,
                    matching_fields TEXT[],
                    ai_comment TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                """
            }
        ).execute()

# ====== 写入推荐榜 ======
def insert_recommendations(user_id, recs):
    for rec in recs:
        supabase.table("recommendations").insert({
            "user_id": user_id,
            "target_id": rec["target_id"],
            "match_score": rec["match_score"],
            "matching_fields": rec["matching_fields"],
            "ai_comment": rec["ai_comment"],
            "created_at": datetime.utcnow().isoformat()
        }).execute()

# ====== 主执行函数 ======
def find_top_matches(user_id):
    # LynkerAI 防火墙检查
    resp = check_permission(user_id)
    if resp["status"] != "ok":
        print(resp)
        return resp

    charts = fetch_all_birthcharts()
    user = next((c for c in charts if c["id"] == user_id), None)
    if not user:
        return {"error": "User not found"}

    user_ai_key = get_user_ai_key(user_id)
    ensure_recommendations_table()
    recommendations = []

    for target in charts:
        if target["id"] == user_id:
            continue

        score, matched = basic_match_score(user, target)

        if user.get("life_summary") and target.get("life_summary"):
            semantic_score = semantic_similarity(user["life_summary"], target["life_summary"], user_ai_key)
            score += WEIGHTS["semantic_similarity"] * semantic_score

        ai_comment = generate_ai_comment(user["name"], target["name"], matched, user_ai_key)

        recommendations.append({
            "target_id": target["id"],
            "target_name": target["name"],
            "match_score": round(score, 2),
            "matching_fields": matched,
            "ai_comment": ai_comment
        })

    recommendations = sorted(recommendations, key=lambda x: x["match_score"], reverse=True)[:10]
    insert_recommendations(user_id, recommendations)

    return {
        "title": "Top 10 同格局推荐榜",
        "user_id": user_id,
        "user_name": user["name"],
        "recommendations": recommendations
    }

# ====== 执行入口 ======
if __name__ == "__main__":
    user_id = 2  # 可以改为任意命主 ID
    result = find_top_matches(user_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("\n✅ 同格局推荐榜已写入 Supabase 数据库（v3.0 多AI版本）。")
