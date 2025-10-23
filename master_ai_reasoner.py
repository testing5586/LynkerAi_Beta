import os
from datetime import datetime
from collections import Counter, defaultdict
from typing import Optional
from supabase import create_client, Client
from master_vault_engine import insert_vault

_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """延迟初始化 Supabase 客户端，带环境变量验证"""
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("❌ 缺少 SUPABASE_URL 或 SUPABASE_KEY 环境变量！")
        
        _client = create_client(url, key)
    return _client

def check_permission(user_id: int):
    """简化的权限检查（如 ai_guard_middleware 不存在时使用）"""
    return {"status": "ok", "user_id": user_id}

# -----------------------------
# 基础数据抓取
# -----------------------------
def fetch_birthcharts():
    try:
        client = get_supabase_client()
        resp = client.table("birthcharts").select("id,name,ziwei_palace,main_star,shen_palace,birth_time").execute()
        return resp.data or []
    except Exception as e:
        print(f"⚠️ 读取 birthcharts 失败: {e}")
        return []

def fetch_match_results():
    try:
        client = get_supabase_client()
        resp = client.table("match_results").select("user_a_id,user_b_id,match_score,matching_fields").execute()
        return resp.data or []
    except Exception:
        return []

def fetch_feedback():
    try:
        client = get_supabase_client()
        resp = client.table("feedback").select("user_id,label,score,created_at").execute()
        return resp.data or []
    except Exception:
        return []

# -----------------------------
# 规则归纳（示例启发式）
# -----------------------------
def derive_population_rules(charts, match_results=None, feedback=None):
    """
    综合分析：主星/命宫组合 + 匹配成功率 + 用户反馈
    输出：rules = { "巳-天府": {"count": 12, "traits": ["稳重","后劲强"], "confidence": 0.62, "match_success_rate": 0.75 } }
    """
    match_results = match_results or []
    feedback = feedback or []
    
    pair_counts = Counter()
    star_counts = Counter()
    palace_counts = Counter()
    
    user_id_to_pair = {}
    for r in charts:
        palace = r.get("ziwei_palace")
        star = r.get("main_star")
        
        if not palace or not star:
            continue
            
        pair = f"{palace}-{star}"
        pair_counts[pair] += 1
        star_counts[star] += 1
        palace_counts[palace] += 1
        user_id_to_pair[r["id"]] = pair

    pair_match_success = defaultdict(lambda: {"total": 0, "success": 0})
    for m in match_results:
        user_a_id = m.get("user_a_id")
        user_b_id = m.get("user_b_id")
        score = m.get("match_score", 0)
        
        for user_id in [user_a_id, user_b_id]:
            if user_id and user_id in user_id_to_pair:
                pair = user_id_to_pair[user_id]
                pair_match_success[pair]["total"] += 1
                if score >= 0.7:
                    pair_match_success[pair]["success"] += 1

    pair_feedback_score = defaultdict(list)
    for f in feedback:
        user_id = f.get("user_id")
        score = f.get("score")
        
        if user_id in user_id_to_pair and score is not None:
            normalized_score = max(0, min(5, float(score)))
            pair = user_id_to_pair[user_id]
            pair_feedback_score[pair].append(normalized_score)

    total = max(1, len(charts))
    rules = {}
    for pair, c in pair_counts.items():
        palace, star = pair.split("-")
        base_conf = c / total
        
        match_stats = pair_match_success.get(pair, {"total": 0, "success": 0})
        match_success_rate = (match_stats["success"] / max(1, match_stats["total"])) if match_stats["total"] > 0 else 0
        
        feedback_scores = pair_feedback_score.get(pair, [])
        avg_feedback = sum(feedback_scores) / len(feedback_scores) if feedback_scores else 0
        
        trait_hint = []
        if star in ("天府","武曲","廉贞","破军","紫微","贪狼"):
            trait_hint.append("性格显著")
        if palace in ("巳","午","卯"):
            trait_hint.append("行动力强")
        if "天府" in star:
            trait_hint.append("后劲强")
        if "廉贞" in star:
            trait_hint.append("规则感/反叛并存")
        if "破军" in star:
            trait_hint.append("破旧立新")
        
        if match_success_rate > 0.7:
            trait_hint.append("缘分佳")
        if avg_feedback > 4.0:
            trait_hint.append("用户满意度高")

        adjusted_conf = base_conf
        if match_success_rate > 0:
            adjusted_conf = (base_conf * 0.6) + (match_success_rate * 0.4)
        if avg_feedback > 0:
            adjusted_conf = (adjusted_conf * 0.8) + ((avg_feedback / 5.0) * 0.2)

        rules[pair] = {
            "count": c,
            "base_confidence": round(base_conf, 4),
            "confidence": round(adjusted_conf, 4),
            "traits": list(set(trait_hint)),
            "match_success_rate": round(match_success_rate, 3),
            "avg_feedback": round(avg_feedback, 2),
            "match_count": match_stats["total"],
            "feedback_count": len(feedback_scores)
        }
    return rules

# -----------------------------
# 基于规则对单用户推理
# -----------------------------
def predict_for_user(user, rules):
    """
    输入：单个用户命盘 + 群体规则（包含匹配/反馈数据）
    输出：可解释预测 dict
    """
    palace = user.get("ziwei_palace")
    star = user.get("main_star")
    
    if not palace or not star:
        return None
        
    pair = f"{palace}-{star}"
    rule = rules.get(pair, {
        "count": 0, 
        "base_confidence": 0.1,
        "confidence": 0.1, 
        "traits": [],
        "match_success_rate": 0,
        "avg_feedback": 0,
        "match_count": 0,
        "feedback_count": 0
    })

    time_window = "未来 6-12 个月"
    conf = rule["confidence"]
    signals = ["主星/命宫组合统计"]
    
    if user.get("shen_palace") == user.get("ziwei_palace"):
        conf = min(0.95, conf + 0.08)
        signals.append("身宫一致加成")
    
    if rule.get("match_count", 0) > 0:
        signals.append(f"匹配数据 ({rule['match_count']} 条)")
    if rule.get("feedback_count", 0) > 0:
        signals.append(f"用户反馈 ({rule['feedback_count']} 条)")

    explanation = {
        "user_id": user["id"],
        "user_name": user.get("name",""),
        "pair": pair,
        "traits": rule["traits"],
        "time_window": time_window,
        "confidence": round(conf, 3),
        "evidence": {
            "population_count": rule["count"],
            "population_ratio": rule.get("base_confidence", 0),
            "adjusted_confidence": rule.get("confidence", 0),
            "match_success_rate": rule.get("match_success_rate", 0),
            "avg_feedback_score": rule.get("avg_feedback", 0),
            "data_sources": {
                "birthcharts": rule["count"],
                "match_results": rule.get("match_count", 0),
                "feedback": rule.get("feedback_count", 0)
            },
            "signals": signals
        }
    }
    return explanation

# -----------------------------
# 结果入库（predictions 表）
# -----------------------------
def save_prediction(record):
    """使用直接 PostgreSQL 连接保存预测（绕过 Supabase PostgREST cache 问题）"""
    try:
        from master_vault_engine import get_db_connection
        import json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO predictions (user_id, user_name, pair, traits, time_window, confidence, evidence, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (user_id, pair) DO UPDATE SET
                confidence = EXCLUDED.confidence,
                evidence = EXCLUDED.evidence,
                created_at = EXCLUDED.created_at
        """, (
            record["user_id"],
            record.get("user_name", ""),
            record["pair"],
            json.dumps(record["traits"], ensure_ascii=False),
            record["time_window"],
            record["confidence"],
            json.dumps(record["evidence"], ensure_ascii=False)
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        print(f"⚠️ 保存预测失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_predictions_batch(records):
    """批量保存预测（使用单个数据库连接）"""
    if not records:
        return
    
    try:
        from master_vault_engine import get_db_connection
        import json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for record in records:
            cursor.execute("""
                INSERT INTO predictions (user_id, user_name, pair, traits, time_window, confidence, evidence, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (user_id, pair) DO UPDATE SET
                    confidence = EXCLUDED.confidence,
                    evidence = EXCLUDED.evidence,
                    created_at = EXCLUDED.created_at
            """, (
                record["user_id"],
                record.get("user_name", ""),
                record["pair"],
                json.dumps(record["traits"], ensure_ascii=False),
                record["time_window"],
                record["confidence"],
                json.dumps(record["evidence"], ensure_ascii=False)
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ 成功保存 {len(records)} 条预测到 PostgreSQL")
        return {"status": "ok", "count": len(records)}
    except Exception as e:
        print(f"⚠️ 批量保存预测失败: {e}")
        import traceback
        traceback.print_exc()
        return None

# -----------------------------
# 重要洞察 -> Vault 加密存档
# -----------------------------
def persist_insight_to_vault(explanations):
    high = [e for e in explanations if e and e.get("confidence", 0) >= 0.5]
    if not high:
        return
    lines = []
    for e in high:
        lines.append(
            f"组合:{e['pair']} 置信:{e['confidence']} 窗口:{e['time_window']} 特质:{'、'.join(e['traits'])}"
        )
    content = "Master Reasoner - 高置信预测快照\n" + "\n".join(lines) + f"\n时间: {datetime.utcnow()}"
    try:
        insert_vault("Reasoner快照 - 高置信预测", content, created_by="Master AI")
        print(f"✅ 已存入 Vault：{len(high)} 条高置信预测")
    except Exception as e:
        print(f"⚠️ Vault 存储失败: {e}")

# -----------------------------
# 公共 API
# -----------------------------
def reason_user(user_id: int):
    gate = check_permission(user_id)
    if gate.get("status") != "ok":
        print(gate)
        return gate

    charts = fetch_birthcharts()
    if not charts:
        return {"status": "error", "msg": "没有命盘数据"}

    match_results = fetch_match_results()
    feedback = fetch_feedback()
    
    rules = derive_population_rules(charts, match_results, feedback)
    u = next((x for x in charts if x["id"] == user_id), None)
    if not u:
        return {"status": "error", "msg": f"未找到用户 {user_id}"}

    explanation = predict_for_user(u, rules)
    if explanation:
        save_prediction(explanation)
        persist_insight_to_vault([explanation])
        return {"status":"ok","prediction":explanation}
    return {"status": "error", "msg": "预测生成失败"}

def reason_all(limit: int = 50):
    charts = fetch_birthcharts()
    if not charts:
        return {"status": "error", "msg": "没有命盘数据"}
    
    match_results = fetch_match_results()
    feedback = fetch_feedback()
    
    print(f"📊 数据加载：{len(charts)} 个命盘，{len(match_results)} 个匹配记录，{len(feedback)} 条反馈")
    
    rules = derive_population_rules(charts, match_results, feedback)

    results = []
    for u in charts[:limit]:
        gate = check_permission(u["id"])
        if gate.get("status") != "ok":
            continue
        e = predict_for_user(u, rules)
        if e:
            results.append(e)

    if results:
        print(f"💾 批量保存 {len(results)} 条预测...")
        save_predictions_batch(results)
    
    persist_insight_to_vault(results)
    return {"status":"ok","count":len(results)}

# -----------------------------
# 辅助：建表 SQL （如缺表时使用）
# -----------------------------
SQL_CREATE_PREDICTIONS = """
create table if not exists predictions (
  id bigint generated by default as identity primary key,
  user_id bigint not null,
  user_name text,
  pair text,
  traits jsonb,
  time_window text,
  confidence numeric,
  evidence jsonb,
  created_at timestamptz default now()
);
"""

if __name__ == "__main__":
    print("🚀 Master AI Reasoner 启动")
    out = reason_all(limit=50)
    print(out)
    print("✅ 完成")
