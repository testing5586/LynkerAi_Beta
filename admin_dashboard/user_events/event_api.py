"""
用户事件追踪 API
Event Tracking API Blueprint
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from .supabase_client import get_client
from .emotion_analyzer import get_analyzer

event_bp = Blueprint('events', __name__, url_prefix='/api')

@event_bp.route('/events/track', methods=['POST'])
def track_event():
    """
    POST /api/events/track
    
    Body:
    {
      "user_id": 3,
      "event_type": "VIEW_PALACE" | "QUESTION" | "FEELING" | "MARK_RESONANCE" | ...,
      "event_payload": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "缺少请求体"}), 400
        
        user_id = data.get("user_id")
        event_type = data.get("event_type")
        event_payload = data.get("event_payload", {})
        
        if not user_id or not event_type:
            return jsonify({"error": "缺少必需字段 user_id 或 event_type"}), 400
        
        # 提取文本用于情绪分析
        text_to_analyze = ""
        if event_type in ["QUESTION", "FEELING"]:
            text_to_analyze = event_payload.get("text", "")
        elif "text" in event_payload:
            text_to_analyze = event_payload["text"]
        
        # 情绪分析
        emotion_label = None
        emotion_score = None
        
        if text_to_analyze:
            analyzer = get_analyzer()
            emotion_label, emotion_score = analyzer.analyze(text_to_analyze)
        
        # 插入数据库
        supabase = get_client()
        if not supabase:
            return jsonify({"error": "数据库连接失败"}), 500
        
        insert_data = {
            "user_id": user_id,
            "event_type": event_type,
            "event_payload": event_payload,
            "emotion_label": emotion_label,
            "emotion_score": float(emotion_score) if emotion_score else None,
            "created_at": datetime.now().isoformat()
        }
        
        result = supabase.table("user_events").insert(insert_data).execute()
        
        if hasattr(result, 'data') and result.data:  # type: ignore
            inserted_id = result.data[0].get("id")  # type: ignore
            
            print(f"✅ 事件已记录: user_id={user_id}, type={event_type}, emotion={emotion_label}")
            
            return jsonify({
                "status": "ok",
                "id": inserted_id,
                "emotion": {
                    "label": emotion_label,
                    "score": emotion_score
                } if emotion_label else None
            })
        else:
            return jsonify({"error": "插入失败"}), 500
            
    except Exception as e:
        print(f"❌ 事件追踪失败: {e}")
        return jsonify({"error": str(e)}), 500


@event_bp.route('/insights/<int:user_id>', methods=['GET'])
def get_insights(user_id):
    """
    GET /api/insights/<user_id>
    
    返回用户画像
    """
    try:
        supabase = get_client()
        if not supabase:
            return jsonify({"error": "数据库连接失败"}), 500
        
        result = supabase.table("user_insights").select("*").eq("user_id", user_id).execute()
        
        if hasattr(result, 'data') and result.data:  # type: ignore
            insight = result.data[0]  # type: ignore
            print(f"✅ 查询用户画像: user_id={user_id}")
            return jsonify(insight)
        else:
            # 返回默认空画像
            default_insight = {
                "user_id": user_id,
                "top_concerns": [],
                "emotion_tendency": "neutral",
                "last_7d_event_count": 0,
                "push_ready": False,
                "updated_at": None
            }
            print(f"⚠️ 用户画像不存在，返回默认值: user_id={user_id}")
            return jsonify(default_insight)
            
    except Exception as e:
        print(f"❌ 查询用户画像失败: {e}")
        return jsonify({"error": str(e)}), 500


@event_bp.route('/events/stats/overview', methods=['GET'])
def get_overview():
    """
    GET /api/events/stats/overview
    
    返回 7 天事件概览
    """
    try:
        supabase = get_client()
        if not supabase:
            return jsonify({"error": "数据库连接失败"}), 500
        
        # 查询最近 7 天事件
        result = supabase.rpc('get_events_last_7d').execute() if hasattr(supabase, 'rpc') else None
        
        # 简化：直接查询所有事件并在 Python 中过滤
        all_events = supabase.table("user_events").select("*").limit(1000).execute()
        
        if not hasattr(all_events, 'data'):
            return jsonify({"total_events": 0, "emotion_distribution": {}})
        
        from datetime import datetime, timedelta
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        events = all_events.data or []  # type: ignore
        recent_events = [
            e for e in events 
            if e.get('created_at') and datetime.fromisoformat(e['created_at'].replace('Z', '+00:00')) > seven_days_ago
        ]
        
        # 统计情绪分布
        emotion_counts = {}
        for event in recent_events:
            label = event.get('emotion_label')
            if label:
                emotion_counts[label] = emotion_counts.get(label, 0) + 1
        
        return jsonify({
            "total_events_7d": len(recent_events),
            "total_events_all": len(events),
            "emotion_distribution": emotion_counts,
            "last_updated": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ 查询事件概览失败: {e}")
        return jsonify({"error": str(e)}), 500
