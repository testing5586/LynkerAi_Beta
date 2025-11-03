# -*- coding: utf-8 -*-
"""
Bazi Agent API - Flask 路由
提供图片识别接口，替代 Node.js Socket.io 方案
"""

from flask import Blueprint, request, jsonify, session
from .bazi_vision_agent import process_bazi_image
import json

bp = Blueprint('bazi_agent_api', __name__, url_prefix='/verify/api')


@bp.route('/run_agent_workflow', methods=['POST'])
def run_agent_workflow():
    """
    运行八字识别工作流
    
    接收: { "imageData": "base64_string" }
    返回: { "success": true/false, "data": {...}, "messages": [...] }
    """
    try:
        data = request.get_json()
        
        if not data or 'imageData' not in data:
            return jsonify({
                "success": False,
                "error": "缺少图片数据"
            }), 400
        
        image_base64 = data['imageData']
        
        # 收集进度消息
        messages = []
        
        def progress_callback(message):
            messages.append(message)
        
        # 调用三层识别系统
        result = process_bazi_image(image_base64, progress_callback)
        
        # 添加进度消息到结果
        result['messages'] = messages
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器错误: {str(e)}",
            "messages": [f"❌ 系统错误: {str(e)}"]
        }), 500


@bp.route('/test_agent', methods=['GET'])
def test_agent():
    """测试端点，验证 Agent 系统是否正常工作"""
    try:
        import os
        
        status = {
            "agent_system": "ok",
            "minimax_api_key": "configured" if os.getenv("MINIMAX_API_KEY") else "missing",
            "openai_api_key": "configured" if os.getenv("OPENAI_API_KEY") else "missing"
        }
        
        return jsonify({
            "success": True,
            "status": status,
            "message": "Bazi Agent System is ready"
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
