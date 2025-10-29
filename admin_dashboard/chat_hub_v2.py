# -*- coding: utf-8 -*-
"""
Chat Hub v2.0 - 真实 AI 协作推理系统
替代旧的模拟系统，集成 Lynker Engine
"""

from lynker_engine import LynkerEngine
from typing import List, Dict

engine = None


def init_engine():
    """初始化 Lynker Engine（延迟加载）"""
    global engine
    if engine is None:
        try:
            engine = LynkerEngine()
            print("OK: Lynker Engine v2.0 initialized successfully")
        except Exception as e:
            print(f"ERROR: Lynker Engine initialization failed: {e}")
            engine = None


def process_message(message: str) -> List[str]:
    """
    处理用户消息，返回三方 AI 的回复列表
    
    参数:
        message: 用户输入的查询
    
    返回:
        [child_response, leader_response, master_response]
    """
    init_engine()
    
    if engine is None:
        return [
            "Child AI: System initializing...",
            "Group Leader: System initializing...",
            "Master AI: System initializing..."
        ]
    
    try:
        responses = engine.process_query(message)
        
        return [
            responses.get("child", "Child AI: No response"),
            responses.get("leader", "Group Leader: No response"),
            responses.get("master", "Master AI: No response")
        ]
    
    except Exception as e:
        print(f"ERROR: Message processing failed: {e}")
        return [
            f"Child AI: Processing error ({str(e)})",
            "Group Leader: Waiting for Child AI to complete...",
            "Master AI: Waiting for team analysis..."
        ]


def get_agent_info() -> Dict:
    """获取 AI Agent 配置信息"""
    init_engine()
    
    if engine is None:
        return {
            "master": {"name": "Master AI", "icon": "[Master]", "model": "Unknown", "role": "Main Control"},
            "leader": {"name": "Group Leader", "icon": "[Leader]", "model": "Unknown", "role": "Task Coordination"},
            "child": {"name": "Child AI", "icon": "[Child]", "model": "Unknown", "role": "Execution Analysis"}
        }
    
    try:
        return engine.get_agent_info()
    except Exception as e:
        print(f"ERROR: Failed to get Agent info: {e}")
        return {}
