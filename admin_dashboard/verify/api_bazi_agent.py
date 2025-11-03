# -*- coding: utf-8 -*-
"""
Bazi Agent API - Flask 路由
提供图片识别接口，替代 Node.js Socket.io 方案
"""

from flask import Blueprint, request, jsonify, session
from .bazi_vision_agent import BaziVisionAgent
from .auto_complete_bazi_json import auto_complete_bazi_json
import json

bp = Blueprint('bazi_agent_api', __name__, url_prefix='/verify/api')


@bp.route('/run_agent_workflow', methods=['POST'])
def run_agent_workflow():
    """
    运行八字识别工作流
    
    接收: { 
        "imageData": "base64_string",
        "environment": {  // 可选
            "country_code": "CN",
            "city": "北京",
            "latitude": 39.904,
            "climate_zone": "温带",
            "humidity_type": "干燥",
            "terrain_type": "内陆"
        }
    }
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
        environment = data.get('environment')  # 获取可选的环境数据
        
        # 日志：显示接收的数据大小
        print(f"[Bazi Agent] 接收图片数据大小: {len(image_base64)} 字符")
        if environment:
            print(f"[Bazi Agent] 接收环境数据: {environment.get('city', 'Unknown')}")
        
        # 收集进度消息
        messages = []
        
        def progress_callback(message):
            messages.append(message)
            print(f"[Bazi Agent] {message}")
        
        # 初始化 Agent 并调用三层识别系统
        agent = BaziVisionAgent()
        result = agent.process_image(image_base64, progress_callback, environment=environment)
        
        # 添加进度消息到结果
        result['messages'] = messages
        
        # 自动补全功能：五行计算、环境信息、AI验证信息
        if result['success'] and result.get('bazi'):
            try:
                # 准备完整的数据结构用于补全
                data_to_complete = {
                    "agent_recognition": {
                        "bazi": result.get('bazi', {}),
                        "full_table": result.get('full_table', {})
                    }
                }
                
                # 如果有环境数据，传递给补全器
                completed_data = auto_complete_bazi_json(data_to_complete, environment)
                
                # 将补全后的数据合并回结果
                result['wuxing'] = completed_data.get('agent_recognition', {}).get('wuxing', {})
                result['ai_verifier'] = completed_data.get('ai_verifier', {})
                if 'environment' in completed_data:
                    result['environment'] = completed_data['environment']
                
                print(f"[Bazi Agent] ✅ 自动补全完成 - 五行: {result['wuxing']}")
                messages.append(f"✅ 五行统计: {', '.join([f'{k}:{v}' for k, v in result['wuxing'].items()])}")
                result['messages'] = messages
                
            except Exception as e:
                print(f"[Bazi Agent] ⚠️ 自动补全失败: {str(e)}")
                # 补全失败不影响主流程，继续返回结果
        
        if result['success']:
            print(f"[Bazi Agent] ✅ 识别成功")
            return jsonify(result), 200
        else:
            print(f"[Bazi Agent] ❌ 识别失败: {result.get('error', 'unknown')}")
            return jsonify(result), 500
    
    except Exception as e:
        print(f"[Bazi Agent] ❌ 异常: {str(e)}")
        import traceback
        traceback.print_exc()
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
            "agent_system": "GPT-4o Vision (v1.2)",
            "openai_api_key": "configured" if os.getenv("OPENAI_API_KEY") else "missing",
            "architecture": "Three-layer (Vision → Normalizer → Formatter)"
        }
        
        return jsonify({
            "success": True,
            "status": status,
            "message": "GPT-4o Bazi Agent System is ready"
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
