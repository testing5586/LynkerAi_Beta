from flask import Flask, request, jsonify
from supabase_init import get_supabase
import json

app = Flask(__name__)
supabase = get_supabase()

@app.route("/api/master-ai/memory", methods=["GET"])
def get_ai_memory():
    """返回子AI记忆内容，可按 user_id 或 tags 过滤"""
    try:
        user_id = request.args.get("user_id")
        tag = request.args.get("tag")
        limit = int(request.args.get("limit", 20))

        query = supabase.table("child_ai_memory").select("*").order("last_interaction", desc=True).limit(limit)
        if user_id:
            query = query.eq("user_id", user_id)
        if tag:
            query = query.contains("tags", f'["{tag}"]')

        response = query.execute()
        data = response.data if hasattr(response, "data") else response
        return jsonify({"status": "ok", "count": len(data), "memories": data})

    except Exception as e:
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
        
        print(f"🔍 搜索关键词: '{keyword}', 限制: {limit}")
        response = supabase.table("child_ai_memory").select("*").ilike("summary", f"%{keyword}%").order("last_interaction", desc=True).limit(limit).execute()
        print(f"📊 Response type: {type(response)}, has data: {hasattr(response, 'data')}")
        data = response.data if hasattr(response, "data") else []
        print(f"✅ 查询返回 {len(data)} 条结果")
        return jsonify({"status": "ok", "count": len(data), "results": data})
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"搜索错误: {error_detail}")
        return jsonify({"status": "error", "message": str(e), "detail": error_detail}), 500


@app.route("/")
def index():
    return "<h3>✅ Master AI Memory API running</h3>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
