# ==========================================================
# LynkerAI TrueChart Verifier v3.1
# AI记忆数据库版（Supabase 写入机制）
# ==========================================================

import json, os, re
from datetime import datetime
from sentence_transformers import SentenceTransformer, util
from supabase import create_client, Client

# ----------------------------------------------------------
# 加载模型
# ----------------------------------------------------------
print("🧠 Loading high-semantic Chinese model (shibing624/text2vec-base-chinese)...")
model = SentenceTransformer("shibing624/text2vec-base-chinese")
print("✅ Model loaded successfully!")

# ----------------------------------------------------------
# 初始化 Supabase 客户端
# ----------------------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("🔗 Connected to Supabase!")
else:
    print("⚠️ Warning: Supabase credentials not found. Results will only be saved locally.")

# ----------------------------------------------------------
# 辅助函数
# ----------------------------------------------------------
def semantic_similarity(a: str, b: str) -> float:
    emb1 = model.encode(a, convert_to_tensor=True)
    emb2 = model.encode(b, convert_to_tensor=True)
    return round(float(util.pytorch_cos_sim(emb1, emb2).item()), 4)

def extract_features_from_chart(chart_text: str):
    patterns = {
        "母缘浅": r"(母|母亲|女性长辈).{0,4}(亡|去世|缘薄|不利)",
        "婚迟": r"(婚|配偶|夫妻).{0,4}(晚|迟|难|破)",
        "事业波折": r"(事|业|工作|官禄).{0,4}(波折|多变|起伏|破)",
        "财运好": r"(财|钱|收入).{0,4}(旺|佳|好|稳)",
        "健康弱": r"(疾|病|身|健康).{0,4}(弱|不佳|受损)",
    }
    features = [k for k, p in patterns.items() if re.search(p, chart_text)]
    raw_terms = re.findall(r"[\u4e00-\u9fa5]{2,6}", chart_text)
    features.extend(list(set(raw_terms[:50])))
    return list(set(features))

# ----------------------------------------------------------
# 单命盘验证逻辑
# ----------------------------------------------------------
def verify_chart(user_id: str, chart_data: dict, life_data: dict):
    chart_text = " ".join([
        chart_data.get("notes", ""),
        chart_data.get("main_star", ""),
        chart_data.get("source", ""),
        chart_data.get("birth_datetime", "")
    ])
    features = extract_features_from_chart(chart_text)
    matched, unmatched = [], []
    total_weight, gained_score = 0, 0

    for ev in life_data.get("events", []):
        desc = ev.get("desc", "")
        weight = ev.get("weight", 1.0)
        total_weight += weight

        best_sim, best_feature = 0.0, None
        for ft in features:
            sim = semantic_similarity(ft, desc)
            if sim > best_sim:
                best_sim, best_feature = sim, ft

        ev["similarity"] = best_sim
        ev["top_match_feature"] = best_feature

        if best_sim >= 0.6:
            matched.append(ev)
            gained_score += weight * best_sim
        else:
            unmatched.append(ev)

    score = round(gained_score / total_weight, 3) if total_weight else 0.0
    confidence = "高" if score >= 0.85 else "中" if score >= 0.65 else "低"

    result = {
        "chart_id": chart_data.get("chart_id", "unknown"),
        "score": score,
        "confidence": confidence,
        "matched_keywords": list({ev["top_match_feature"] for ev in matched if ev.get("top_match_feature")}),
        "verified_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # ✅ 写入 Supabase
    if supabase:
        try:
            supabase.table("verified_charts").insert({
                "user_id": user_id,
                "chart_id": result["chart_id"],
                "score": result["score"],
                "confidence": result["confidence"],
                "matched_keywords": result["matched_keywords"],
                "verified_at": result["verified_at"]
            }).execute()
            print(f"🧾 Saved verification record for {user_id} → {result['chart_id']}")
        except Exception as e:
            print("⚠️ Supabase insert error:", e)

    return result

# ----------------------------------------------------------
# 多命盘组合验证
# ----------------------------------------------------------
def verify_multiple_charts(user_id: str, charts: list, life_data: dict):
    combo_results = [verify_chart(user_id, ch, life_data) for ch in charts]
    combo_results.sort(key=lambda x: x["score"], reverse=True)
    best = combo_results[0]["chart_id"] if combo_results else None

    output = {
        "user_id": user_id,
        "combos": combo_results,
        "best_match": best,
        "verified_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    json.dump(output, open("./data/verified_birth_profiles.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    return output

# ----------------------------------------------------------
# 手动测试
# ----------------------------------------------------------
if __name__ == "__main__":
    os.makedirs("./data", exist_ok=True)
    chart_A = {
        "chart_id": "c_A",
        "source": "wenmo",
        "birth_datetime": "1975-05-10 23:10",
        "main_star": "天府",
        "notes": "命宫在巳，母缘浅，婚迟，事业初有波折后成，财运中年见旺"
    }
    chart_B = {
        "chart_id": "c_B",
        "source": "wenmo",
        "birth_datetime": "1975-05-10 22:45",
        "main_star": "紫微",
        "notes": "命宫在辰，父母缘厚，婚早但破，事业稳中有进"
    }
    chart_C = {
        "chart_id": "c_C",
        "source": "wenmo",
        "birth_datetime": "1975-05-10 23:30",
        "main_star": "武曲",
        "notes": "命宫在午，母缘浅，婚姻迟成，事业起伏，财运后旺"
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
    charts = [chart_A, chart_B, chart_C]
    print(json.dumps(verify_multiple_charts("u_demo", charts, life_demo), ensure_ascii=False, indent=2))
