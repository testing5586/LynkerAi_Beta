# ==========================================================
# LynkerAI TrueChart Verifier v2.0
# 中文语义比对版（免费模型：uer/sbert-base-chinese-nli）
# ==========================================================

import json, os
from datetime import datetime
from sentence_transformers import SentenceTransformer, util

# ----------------------------------------------------------------
# 初始化免费中文模型
# ----------------------------------------------------------------
print("🧠 Loading free Chinese semantic model (uer/sbert-base-chinese-nli)...")
model = SentenceTransformer('uer/sbert-base-chinese-nli')
print("✅ Model loaded successfully!")

# ----------------------------------------------------------------
# 主函数
# ----------------------------------------------------------------
def semantic_similarity(text1: str, text2: str) -> float:
    """语义相似度（0~1）"""
    emb1 = model.encode(text1, convert_to_tensor=True)
    emb2 = model.encode(text2, convert_to_tensor=True)
    score = util.pytorch_cos_sim(emb1, emb2).item()
    return round(float(score), 4)


def verify_chart(user_id):
    base_dir = "./data"
    chart_file = os.path.join(base_dir, f"{user_id}_chart.json")
    life_file = os.path.join(base_dir, f"{user_id}_life.json")
    verified_file = os.path.join(base_dir, "verified_birth_profiles.json")

    if not os.path.exists(chart_file) or not os.path.exists(life_file):
        return {"status": "error", "msg": "缺少命盘或人生资料文件"}

    with open(chart_file, "r", encoding="utf-8") as f:
        chart_data = json.load(f)
    with open(life_file, "r", encoding="utf-8") as f:
        life_data = json.load(f)

    # 命盘文本化（供比对）
    chart_text = " ".join([
        chart_data.get("notes", ""),
        chart_data.get("main_star", ""),
        chart_data.get("source", ""),
    ])

    matched, unmatched = [], []
    total_weight, gained_score = 0, 0

    for ev in life_data.get("events", []):
        desc = ev.get("desc", "")
        weight = ev.get("weight", 1.0)
        total_weight += weight
        sim = semantic_similarity(chart_text, desc)
        ev["similarity"] = sim

        if sim >= 0.65:  # 相似度阈值
            matched.append(ev)
            gained_score += weight * sim
        else:
            unmatched.append(ev)

    score = round(gained_score / total_weight, 3) if total_weight else 0.0
    confidence = "高" if score >= 0.85 else "中" if score >= 0.65 else "低"

    # life_tags 提取
    life_tags = {
        "career_type": life_data.get("career_type", ""),
        "marriage_status": life_data.get("marriage_status", ""),
        "children": life_data.get("children", 0),
        "study_abroad": any("留学" in ev.get("desc", "") for ev in life_data.get("events", [])),
        "major_accident": next((ev.get("desc") for ev in life_data.get("events", [])
                                if any(k in ev.get("desc", "") for k in ["病", "伤", "车祸", "手术"])), None)
    }

    result = {
        "user_id": user_id,
        "verified_chart_id": chart_data.get("chart_id", "unknown"),
        "score": score,
        "confidence": confidence,
        "matched_events": matched,
        "unmatched_events": unmatched,
        "life_tags": life_tags,
        "status": "verified" if score >= 0.75 else "unverified",
        "verified_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    os.makedirs(base_dir, exist_ok=True)
    verified_data = []
    if os.path.exists(verified_file):
        try:
            verified_data = json.load(open(verified_file, encoding="utf-8"))
        except:
            verified_data = []
    existing = next((r for r in verified_data if r["user_id"] == user_id), None)
    if existing:
        existing.update(result)
    else:
        verified_data.append(result)
    json.dump(verified_data, open(verified_file, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return result


# ----------------------------------------------------------------
# 手动测试
# ----------------------------------------------------------------
if __name__ == "__main__":
    os.makedirs("./data", exist_ok=True)

    chart_demo = {
        "chart_id": "c_demo",
        "source": "wenmo",
        "birth_datetime": "1975-05-10 23:10",
        "main_star": "天府",
        "notes": "命宫在巳，武曲、天同格局，母缘浅，事业早起波折后成"
    }

    life_demo = {
        "career_type": "设计行业",
        "marriage_status": "晚婚",
        "children": 1,
        "events": [
            {"desc": "2003年母亲去世", "weight": 2.0},
            {"desc": "2006年海外留学", "weight": 1.0},
            {"desc": "2010年获设计奖项", "weight": 1.5},
            {"desc": "婚姻晚成，妻子年长八岁", "weight": 1.2}
        ]
    }

    with open("./data/u_demo_chart.json", "w", encoding="utf-8") as f:
        json.dump(chart_demo, f, ensure_ascii=False, indent=2)
    with open("./data/u_demo_life.json", "w", encoding="utf-8") as f:
        json.dump(life_demo, f, ensure_ascii=False, indent=2)

    print(json.dumps(verify_chart("u_demo"), ensure_ascii=False, indent=2))
