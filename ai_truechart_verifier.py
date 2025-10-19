# ==========================================================
# LynkerAI TrueChart Verifier v3.2
# AI记忆数据库版（Supabase 写入机制）
# ==========================================================

import json, os, re
from datetime import datetime
from sentence_transformers import SentenceTransformer, util
from supabase_init import init_supabase

# ----------------------------------------------------------
# 加载模型
# ----------------------------------------------------------
print("🧠 Loading high-semantic Chinese model (shibing624/text2vec-base-chinese)...")
model = SentenceTransformer("shibing624/text2vec-base-chinese")
print("✅ Model loaded successfully!")

# ----------------------------------------------------------
# 初始化 Supabase 客户端
# ----------------------------------------------------------
supabase = init_supabase()

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
# 智能权重学习系统
# ----------------------------------------------------------
def update_event_weights(supabase_client, unmatched_events):
    """动态调整人生事件权重，基于相似度进行智能学习"""
    if supabase_client is None:
        return
    
    for e in unmatched_events:
        new_weight = e["weight"]
        sim = e["similarity"]
        
        # 智能权重调整策略
        if sim > 0.6:
            # 相似度高但未匹配，增加权重
            new_weight = min(e["weight"] + 0.1, 3.0)
        elif sim < 0.3:
            # 相似度极低，降低权重
            new_weight = max(e["weight"] - 0.05, 0.5)
        
        e["weight"] = new_weight
        
        try:
            supabase_client.table("life_event_weights").upsert({
                "event_desc": e["desc"],
                "weight": new_weight,
                "similarity": sim,
                "updated_at": datetime.now().isoformat()
            }).execute()
            print(f"📈 权重更新：{e['desc']} → {new_weight:.2f}")
        except Exception as err:
            print(f"⚠️ 权重保存失败：{e['desc']} | {err}")

def save_life_tags(supabase_client, user_id, life_tags):
    """保存或更新用户的 life_tags（人生标签）"""
    if supabase_client is None:
        return
    
    try:
        supabase_client.table("user_life_tags").upsert({
            "user_id": user_id,
            **life_tags,
            "updated_at": datetime.now().isoformat()
        }).execute()
        print(f"💾 已保存 life_tags → {user_id}")
    except Exception as err:
        print(f"⚠️ 保存 life_tags 失败: {err}")

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

    # ✅ 智能权重学习：根据未匹配事件的相似度动态调整权重
    unmatched_events = unmatched
    if unmatched_events:
        print(f"\n🧠 智能权重学习中... ({len(unmatched_events)} 个未匹配事件)")
        update_event_weights(supabase, unmatched_events)
    
    # ✅ 构建并保存用户 life_tags 到数据库
    life_tags = {
        "career_type": life_data.get("career_type", ""),
        "marriage_status": life_data.get("marriage_status", ""),
        "children": life_data.get("children", 0),
        "event_count": len(life_data.get("events", []))
    }
    print(f"\n💾 保存用户人生标签...")
    save_life_tags(supabase, user_id, life_tags)

    # ✅ 写入验证结果到 Supabase
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
# 主入口函数（供外部调用）
# ----------------------------------------------------------
def run_truechart_verifier(user_id="u_demo", supabase_client=None):
    """
    真命盘验证主函数
    参数：
        user_id: 用户ID
        supabase_client: Supabase 客户端（可选）
    返回：
        验证结果的 JSON 对象
    """
    os.makedirs("./data", exist_ok=True)
    
    # 示例测试数据
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
    
    # 使用传入的 supabase 客户端或全局的 supabase
    global supabase
    if supabase_client:
        supabase = supabase_client
    
    result = verify_multiple_charts(user_id, charts, life_demo)
    return result

# ----------------------------------------------------------
# 手动测试
# ----------------------------------------------------------
if __name__ == "__main__":
    result = run_truechart_verifier("u_demo")
    print(json.dumps(result, ensure_ascii=False, indent=2))
