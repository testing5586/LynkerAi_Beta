"""
LynkerAI TMS (Trusted Metaphysics System) v1.0
主验证器 API - 负责命盘签章验证、置信投票、区域适配
"""
from flask import Flask, request, jsonify
import datetime
import hashlib
import os
import hmac

app = Flask(__name__)

TMS_SECRET = os.getenv("TMS_SECRET_KEY", "default_tms_secret_change_me")

def generate_chart_hash(chart_data: dict) -> str:
    """生成命盘哈希值"""
    chart_str = str(sorted(chart_data.items()))
    return hashlib.sha256(chart_str.encode()).hexdigest()

def verify_signature(public_key: str, payload: str, signature: str) -> bool:
    """
    验证AI签章（简化版）
    生产环境建议使用 RSA 或 Ed25519 公钥签名
    """
    if not signature or not signature.startswith("AI_"):
        return False
    
    expected = hmac.new(
        TMS_SECRET.encode(),
        f"{public_key}:{payload}".encode(),
        hashlib.sha256
    ).hexdigest()
    
    return signature == f"AI_{expected}"

def create_signature(public_key: str, payload: str) -> str:
    """创建AI签章"""
    sig = hmac.new(
        TMS_SECRET.encode(),
        f"{public_key}:{payload}".encode(),
        hashlib.sha256
    ).hexdigest()
    return f"AI_{sig}"

@app.route("/api/tms/verify", methods=["POST"])
def verify_chart():
    """
    验证命盘签章
    POST /api/tms/verify
    Body: {
        "public_key": "child_ai_001",
        "payload": "chart_hash_123",
        "signature": "AI_xxxx"
    }
    """
    try:
        data = request.get_json(force=True)
        
        if not data:
            return jsonify({
                "verified": False,
                "error": "缺少请求数据"
            }), 400
        
        public_key = data.get("public_key")
        payload = data.get("payload")
        signature = data.get("signature")
        
        if not all([public_key, payload, signature]):
            return jsonify({
                "verified": False,
                "error": "缺少必要参数: public_key, payload, signature"
            }), 400
        
        is_valid = verify_signature(public_key, payload, signature)
        
        if is_valid:
            return jsonify({
                "verified": True,
                "timestamp": datetime.datetime.now().isoformat(),
                "chart_hash": payload,
                "verifier": "TMS_Master_v1.0"
            })
        else:
            return jsonify({
                "verified": False,
                "error": "签章验证失败",
                "timestamp": datetime.datetime.now().isoformat()
            }), 403
            
    except Exception as e:
        return jsonify({
            "verified": False,
            "error": f"验证异常: {str(e)}"
        }), 500

@app.route("/api/tms/sign", methods=["POST"])
def sign_chart():
    """
    为命盘生成签章
    POST /api/tms/sign
    Body: {
        "public_key": "child_ai_001",
        "chart_data": {...}
    }
    """
    try:
        data = request.get_json(force=True)
        
        public_key = data.get("public_key")
        chart_data = data.get("chart_data")
        
        if not public_key or not chart_data:
            return jsonify({
                "error": "缺少参数: public_key 或 chart_data"
            }), 400
        
        chart_hash = generate_chart_hash(chart_data)
        signature = create_signature(public_key, chart_hash)
        
        return jsonify({
            "chart_hash": chart_hash,
            "signature": signature,
            "public_key": public_key,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": f"签章生成失败: {str(e)}"
        }), 500

@app.route("/api/tms/health", methods=["GET"])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "service": "TMS Master Validator",
        "version": "1.0",
        "timestamp": datetime.datetime.now().isoformat()
    })

if __name__ == "__main__":
    print("🔐 LynkerAI TMS Master Validator v1.0 启动")
    print(f"📍 监听端口: 8080")
    print(f"🔑 密钥状态: {'✅ 已配置' if TMS_SECRET != 'default_tms_secret_change_me' else '⚠️  使用默认密钥（不安全）'}")
    app.run(host="0.0.0.0", port=8080, debug=False)
