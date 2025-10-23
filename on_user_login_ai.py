import os
from flask import Flask, request, jsonify
from datetime import datetime
from master_ai_reasoner import reason_user
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

LOG_PATH = "logs/user_login_activity.log"
os.makedirs("logs", exist_ok=True)

def write_log(msg):
    """写入登录活动日志"""
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")

def get_top_10_recommendations():
    """从 recommendations 表获取 Top 10 推荐榜"""
    try:
        resp = client.table("recommendations").select(
            "user_a_name,user_b_name,match_score,matching_fields"
        ).order("match_score", desc=True).limit(10).execute()
        return resp.data or []
    except Exception as e:
        print("⚠️ 无法获取推荐榜:", e)
        return []

def refresh_recommendations_for_user(user_id):
    """刷新指定用户的推荐榜（基于最新预测结果）"""
    try:
        from match_palace import calculate_match_score
        
        user_res = client.table("birthcharts").select("*").eq("id", user_id).execute()
        if not user_res.data:
            return 0
        
        user_chart = user_res.data[0]
        all_charts = client.table("birthcharts").select("*").neq("id", user_id).execute().data
        
        updated_count = 0
        for target in all_charts:
            score, fields = calculate_match_score(user_chart, target)
            if score > 0:
                try:
                    client.table("recommendations").upsert({
                        "user_a_id": user_id,
                        "user_a_name": user_chart["name"],
                        "user_b_id": target["id"],
                        "user_b_name": target["name"],
                        "match_score": score,
                        "matching_fields": fields,
                        "created_at": datetime.utcnow().isoformat()
                    }).execute()
                    updated_count += 1
                except Exception:
                    pass
        
        return updated_count
    except Exception as e:
        print(f"⚠️ 刷新推荐榜失败: {e}")
        return 0

@app.route("/login_refresh", methods=["POST"])
def login_refresh():
    """
    用户登录触发推理引擎
    POST /login_refresh
    Body: {"user_id": 2}
    """
    data = request.json
    user_id = data.get("user_id")
    
    if not user_id:
        return jsonify({"error": "缺少 user_id 参数"}), 400

    write_log(f"🔔 用户 {user_id} 登录触发推理引擎...")

    try:
        result = reason_user(user_id)
    except Exception as e:
        write_log(f"❌ 推理错误: {e}")
        return jsonify({"status": "error", "msg": str(e)}), 500

    prediction = result.get("prediction", {})
    conf = prediction.get("confidence", 0)
    refreshed = False
    refresh_count = 0

    if conf >= 0.6:
        write_log(f"✅ 用户 {user_id} 推理置信度高({conf})，刷新推荐榜...")
        refresh_count = refresh_recommendations_for_user(user_id)
        refreshed = True
        write_log(f"📊 已更新 {refresh_count} 条推荐记录")

    top10 = get_top_10_recommendations()
    write_log(f"✅ 登录结果: user={user_id}, conf={conf}, refreshed={refreshed}, top10_count={len(top10)}")

    return jsonify({
        "status": "ok",
        "user_id": user_id,
        "prediction": prediction,
        "refreshed": refreshed,
        "refresh_count": refresh_count,
        "recommendations": top10
    })

@app.route("/health", methods=["GET"])
def health():
    """健康检查"""
    return jsonify({"status": "ok", "service": "Master AI Login Trigger"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print(f"🚀 Master AI 登录触发推理模块启动 (端口 {port})")
    print(f"📝 日志路径: {LOG_PATH}")
    app.run(host="0.0.0.0", port=port)
