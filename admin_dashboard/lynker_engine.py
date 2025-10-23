"""
Lynker Engine v2.0 - 核心智能协作引擎
负责：协调 Master AI、Group Leader、Child AI 三方协作
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

from ai_agents.master_agent import MasterAgent
from ai_agents.group_leader_agent import GroupLeaderAgent
from ai_agents.child_agent import ChildAgent


class LynkerEngine:
    """LynkerAI 核心智能协作引擎"""
    
    def __init__(self):
        config_path = Path(__file__).parent / "config.json"
        
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        
        self.master = MasterAgent(self.config)
        self.leader = GroupLeaderAgent(self.config)
        self.child = ChildAgent(self.config)
        
        self.enabled = self.config["ai_collaboration"]["enabled"]
        self.timeout = self.config["ai_collaboration"]["timeout_seconds"]
    
    def process_query(self, user_query: str) -> Dict[str, str]:
        """
        处理用户查询，返回三方 AI 的完整对话
        
        返回格式：
        {
            "child": "Child AI 的分析结果",
            "leader": "Group Leader 的协调报告",
            "master": "Master AI 的最终结论"
        }
        """
        if not self.enabled:
            return self._fallback_response(user_query)
        
        try:
            child_response = self.child.process(user_query)
            
            leader_response = self.leader.process(user_query, self.child)
            
            vault_context = self._get_vault_context(user_query)
            
            master_response = self.master.process(
                user_query, 
                leader_response, 
                vault_context
            )
            
            return {
                "child": child_response,
                "leader": leader_response,
                "master": master_response
            }
        
        except Exception as e:
            print(f"❌ Lynker Engine 处理失败: {e}")
            return self._fallback_response(user_query)
    
    def _get_vault_context(self, query: str) -> Optional[str]:
        """从 Master Vault 获取相关知识（简化版）"""
        try:
            from master_vault_engine import list_vault_entries
            
            entries = list_vault_entries()
            
            if entries:
                recent = entries[:3]
                context = "近期知识库发现：\n"
                for entry in recent:
                    title = entry[1] if len(entry) > 1 else "未知"
                    context += f"- {title}\n"
                return context
        except Exception as e:
            print(f"⚠️ 无法获取 Vault 知识: {e}")
        
        return None
    
    def _fallback_response(self, user_query: str) -> Dict[str, str]:
        """降级响应（AI 不可用时）"""
        return {
            "child": f"{self.child.icon} {self.child.name}: 正在分析数据库...",
            "leader": f"{self.leader.icon} {self.leader.name}: 协调任务中...",
            "master": f"{self.master.icon} {self.master.name}: 系统暂时无法完成深度推理。"
        }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """获取所有 Agent 的配置信息"""
        return {
            "master": {
                "name": self.master.name,
                "icon": self.master.icon,
                "model": self.master.model,
                "role": self.config["agents"]["master"]["role"]
            },
            "leader": {
                "name": self.leader.name,
                "icon": self.leader.icon,
                "model": self.leader.model,
                "role": self.config["agents"]["leader"]["role"]
            },
            "child": {
                "name": self.child.name,
                "icon": self.child.icon,
                "model": self.child.model,
                "role": self.config["agents"]["child"]["role"]
            }
        }
