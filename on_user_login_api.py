import os
import requests
import json
from datetime import datetime
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
# Google OAuth 回调处理
# ===============================
def handle_google_callback(code):
    """处理 Google OAuth 回调"""
    
    token_url = "https://oauth2.googleapis.com/token"
    
    data = {
        "code": code,
        "client_id": os.getenv("VITE_GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("VITE_GOOGLE_CLIENT_SECRET"),
        "redirect_uri": os.getenv("VITE_GOOGLE_REDIRECT_URI"),
        "grant_type": "authorization_code",
    }
    
    try:
        res = requests.post(token_url, data=data)
        
        if res.status_code != 200:
            return f"❌ Token 交换失败：{res.text}", 400
        
        tokens = res.json()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        
        if not access_token:
            return "❌ 未获取到 access_token", 400
        
        user_info_res = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo?alt=json",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if user_info_res.status_code != 200:
            return f"❌ 获取用户信息失败：{user_info_res.text}", 400
        
        user_info = user_info_res.json()
        email = user_info.get("email", "unknown")
        user_name = user_info.get("name", email.split("@")[0])
        user_id = email.split("@")[0]
        
        try:
            result = supabase.table("users").upsert({
                "name": user_id,
                "email": email,
                "drive_email": email,
                "drive_access_token": access_token,
                "drive_connected": True,
                "updated_at": datetime.now().isoformat()
            }).execute()
            
            print(f"✅ 用户 {email} 授权成功，已保存到 Supabase")
            
        except Exception as e:
            print(f"⚠️ Supabase 保存失败：{e}")
            return f"⚠️ 数据保存失败：{str(e)}", 500
        
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google Drive 绑定成功</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
            text-align: center;
        }}
        .success-icon {{
            font-size: 64px;
            margin-bottom: 20px;
        }}
        h2 {{
            color: #10b981;
            margin-bottom: 20px;
            font-size: 28px;
        }}
        .info {{
            background: #f3f4f6;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: left;
        }}
        .info-item {{
            margin: 10px 0;
            font-size: 14px;
            color: #374151;
        }}
        .info-item strong {{
            color: #1f2937;
        }}
        .token {{
            font-family: 'Courier New', monospace;
            background: #e5e7eb;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
        }}
        .close-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            margin-top: 20px;
            transition: background 0.3s;
        }}
        .close-btn:hover {{
            background: #5568d3;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">✅</div>
        <h2>Google Drive 绑定成功！</h2>
        
        <div class="info">
            <div class="info-item">
                <strong>📧 用户邮箱：</strong><br>
                {email}
            </div>
            <div class="info-item">
                <strong>👤 用户名称：</strong><br>
                {user_name}
            </div>
            <div class="info-item">
                <strong>🔑 Access Token：</strong><br>
                <span class="token">{access_token[:12]}...</span>
            </div>
            <div class="info-item">
                <strong>💾 存储状态：</strong><br>
                已保存到 Supabase.users 表
            </div>
        </div>
        
        <p style="color: #6b7280; font-size: 14px; margin-top: 20px;">
            🎉 您现在可以关闭此页面，返回应用继续操作。
        </p>
        
        <button class="close-btn" onclick="window.close()">关闭窗口</button>
    </div>
    
    <script>
        setTimeout(() => {{
            if (window.opener) {{
                window.opener.postMessage({{
                    type: 'GOOGLE_OAUTH_SUCCESS',
                    email: '{email}',
                    userId: '{user_id}'
                }}, '*');
            }}
        }}, 500);
    </script>
</body>
</html>
        """, 200
        
    except Exception as e:
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>授权失败</title>
    <style>
        body {{
            font-family: sans-serif;
            background: #fee;
            padding: 40px;
            text-align: center;
        }}
        .error {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            max-width: 500px;
            margin: 0 auto;
        }}
    </style>
</head>
<body>
    <div class="error">
        <h2>❌ 授权失败</h2>
        <p>错误信息：{str(e)}</p>
        <p>请返回应用重试。</p>
    </div>
</body>
</html>
        """, 500


# ===============================
# Flask API 路由
# ===============================
@app.route("/", methods=["GET"])
@app.route("/callback", methods=["GET"])
@app.route("/oauth2callback", methods=["GET"])
def google_callback():
    """Google OAuth 回调端点（支持多个路由）"""
    
    code = request.args.get("code")
    
    if not code:
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>LynkerAI API</title>
    <style>
        body {
            font-family: sans-serif;
            background: #f9fafb;
            padding: 40px;
            text-align: center;
        }
        .info {
            background: white;
            padding: 30px;
            border-radius: 10px;
            max-width: 500px;
            margin: 0 auto;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="info">
        <h2>🔐 LynkerAI API</h2>
        <p>此服务用于处理 Google OAuth 回调。</p>
        <p>如需授权，请从应用开始 OAuth 流程。</p>
    </div>
</body>
</html>
        """, 200
    
    return handle_google_callback(code)


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


@app.route("/api/master-ai/memory", methods=["GET"])
def get_ai_memory():
    """返回子AI记忆内容，可按 user_id 或 tags 过滤"""
    try:
        user_id = request.args.get("user_id")
        tag = request.args.get("tag")
        limit = int(request.args.get("limit", 20))
        
        print(f"🧠 Memory API 请求 → user_id={user_id}, tag={tag}, limit={limit}")

        query = supabase.table("child_ai_memory").select("*").order("last_interaction", desc=True).limit(limit)
        if user_id:
            query = query.eq("user_id", user_id)
        if tag:
            query = query.filter("tags", "cs", json.dumps([tag]))

        response = query.execute()
        data = response.data if hasattr(response, "data") else response
        
        print(f"✅ 返回 {len(data)} 条记忆记录")
        return jsonify({"status": "ok", "count": len(data), "memories": data})

    except Exception as e:
        print(f"⚠️ Memory API 错误: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/master-ai/memory/search", methods=["GET"])
def search_memory():
    """模糊搜索 summary 内容"""
    keyword = request.args.get("q", "")
    limit = int(request.args.get("limit", 20))
    
    if not keyword:
        return jsonify({"status": "error", "message": "Missing query parameter 'q'"}), 400

    try:
        if not supabase:
            return jsonify({"status": "error", "message": "Supabase not available"}), 500
        
        print(f"🔍 Memory 搜索 → 关键词='{keyword}', limit={limit}")
        response = supabase.table("child_ai_memory").select("*").ilike("summary", f"%{keyword}%").order("last_interaction", desc=True).limit(limit).execute()
        data = response.data if hasattr(response, "data") else []
        
        print(f"✅ 搜索返回 {len(data)} 条结果")
        return jsonify({"status": "ok", "count": len(data), "results": data})
        
    except Exception as e:
        import traceback
        print(f"⚠️ 搜索错误: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/master-ai-memory")
def master_ai_dashboard():
    """Master AI Memory Dashboard - React 可视化界面"""
    try:
        with open("static/master_ai_dashboard.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({"error": "Dashboard 文件未找到"}), 404

@app.route("/health", methods=["GET"])
def health_check():
    """健康检查端点"""
    return jsonify({
        "status": "healthy",
        "service": "lynkerai_api",
        "endpoints": {
            "oauth_callback": ["/", "/callback", "/oauth2callback"],
            "api": ["/login_refresh", "/health"],
            "memory_api": ["/api/master-ai/memory", "/api/master-ai/memory/search"],
            "dashboard": ["/master-ai-memory"]
        }
    }), 200


# ===============================
# 启动服务
# ===============================
if __name__ == "__main__":
    import sys
    port = 5000
    if len(sys.argv) > 1 and sys.argv[1] == '--port' and len(sys.argv) > 2:
        port = int(sys.argv[2])
    app.run(host="0.0.0.0", port=port)
