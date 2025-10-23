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
            print("✅ Lynker Engine v2.0 初始化成功")
        except Exception as e:
            print(f"❌ Lynker Engine 初始化失败: {e}")
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
            "🤖 Child AI: 系统初始化中...",
            "🧩 Group Leader: 系统初始化中...",
            "🧠 Master AI: 系统初始化中..."
        ]
    
    try:
        responses = engine.process_query(message)
        
        return [
            responses.get("child", "🤖 Child AI: 无响应"),
            responses.get("leader", "🧩 Group Leader: 无响应"),
            responses.get("master", "🧠 Master AI: 无响应")
        ]
    
    except Exception as e:
        print(f"❌ 处理消息失败: {e}")
        return [
            f"🤖 Child AI: 处理出错 ({str(e)})",
            "🧩 Group Leader: 等待 Child AI 完成...",
            "🧠 Master AI: 等待团队分析..."
        ]


def get_agent_info() -> Dict:
    """获取 AI Agent 配置信息"""
    init_engine()
    
    if engine is None:
        return {
            "master": {"name": "Master AI", "icon": "🧠", "model": "未知", "role": "主控推理"},
            "leader": {"name": "Group Leader", "icon": "🧩", "model": "未知", "role": "任务协调"},
            "child": {"name": "Child AI", "icon": "🤖", "model": "未知", "role": "执行分析"}
        }
    
    try:
        return engine.get_agent_info()
    except Exception as e:
        print(f"❌ 获取 Agent 信息失败: {e}")
        return {}
