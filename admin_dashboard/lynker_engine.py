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
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        处理用户查询，返回三方 AI 的完整对话（v2.1 - 动态命理分析）
        
        返回格式：
        {
            "child": "Child AI 的分析结果",
            "leader": "Group Leader 的协调报告",
            "master": "Master AI 的最终结论",
            "vault_saved": bool,
            "superintendent_notified": bool
        }
        """
        if not self.enabled:
            return self._fallback_response(user_query)
        
        try:
            child_result = self.child.analyze_pattern(user_query)
            child_response = f"{self.child.icon} {self.child.name}: {child_result.get('summary', '分析中...')}"
            
            leader_report = self.leader.coordinate(user_query, [child_result])
            leader_response = f"{self.leader.icon} {self.leader.name}: {leader_report.get('summary', '协调中...')}"
            
            vault_context = self._get_vault_context(user_query)
            
            master_result = self.master.reason(
                user_query, 
                leader_report, 
                vault_context
            )
            master_response = f"{self.master.icon} {self.master.name}: {master_result.get('conclusion', '推理中...')}"
            
            vault_saved = False
            superintendent_notified = False
            
            if master_result.get("should_save_to_vault", False):
                vault_saved = self._save_to_vault(user_query, master_result, leader_report)
                
                if vault_saved and master_result.get("confidence", 0) >= 0.80:
                    superintendent_notified = self._notify_superintendent(master_result)
            
            return {
                "child": child_response,
                "leader": leader_response,
                "master": master_response,
                "vault_saved": vault_saved,
                "superintendent_notified": superintendent_notified,
                "confidence": master_result.get("confidence", 0),
                "sample_size": master_result.get("sample_size", 0)
            }
        
        except Exception as e:
            print(f"❌ Lynker Engine 处理失败: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_response(user_query)
    
    def _get_vault_context(self, query: str) -> Optional[str]:
        """从 Master Vault 获取相关知识（简化版）"""
        try:
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            
            from master_vault_engine import list_vault_entries
            
            entries = list_vault_entries(role="Superintendent Admin")
            
            if not entries:
                print("ℹ️ Master Vault 暂无知识条目")
                return None
            
            recent = entries[:3]
            context = "近期 Vault 知识库发现：\n"
            for entry in recent:
                title = entry[1] if len(entry) > 1 else "未知"
                created_at = entry[4] if len(entry) > 4 else "未知时间"
                context += f"- {title} ({created_at})\n"
            
            return context
        except ImportError as e:
            print(f"⚠️ Master Vault Engine 未安装: {e}")
            return None
        except Exception as e:
            print(f"⚠️ 无法获取 Vault 知识: {e}")
            return None
    
    def _save_to_vault(self, user_query: str, master_result: Dict, leader_report: Dict) -> bool:
        """保存高信度发现到 Master Vault"""
        try:
            import sys
            from datetime import datetime
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            
            from master_vault_engine import save_to_vault
            
            title = f"命盘规律对比分析报告 #{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            content = f"""
查询：{user_query}

样本量：{master_result.get('sample_size', 0)} 份
置信度：{master_result.get('confidence', 0):.2%}
规律相符率：{leader_report.get('conformity_rate', 0):.2%}

核心发现：
{chr(10).join(['- ' + d for d in master_result.get('new_discoveries', [])])}

Master AI 结论：
{master_result.get('conclusion', '未知')}
"""
            
            save_to_vault(
                title=title,
                content=content,
                author="Master AI",
                role="Superintendent Admin"
            )
            
            print(f"✅ 已将高信度发现存入 Master Vault：{title}")
            return True
            
        except Exception as e:
            print(f"⚠️ Vault 存储失败: {e}")
            return False
    
    def _notify_superintendent(self, master_result: Dict) -> bool:
        """通知 Superintendent Admin 新规律发现"""
        try:
            confidence = master_result.get("confidence", 0)
            sample_size = master_result.get("sample_size", 0)
            new_discoveries = master_result.get("new_discoveries", [])
            
            notification = f"""
🧠 新规律已验证！

置信度：{confidence:.2%}
样本量：{sample_size} 份
新发现：{', '.join(new_discoveries[:2]) if new_discoveries else '无'}

请前往 Master Vault 查看完整报告。
"""
            
            print(notification)
            
            return True
            
        except Exception as e:
            print(f"⚠️ Superintendent 通知失败: {e}")
            return False
    
    def _fallback_response(self, user_query: str) -> Dict[str, Any]:
        """降级响应（AI 不可用时）"""
        return {
            "child": f"{self.child.icon} {self.child.name}: 正在分析数据库...",
            "leader": f"{self.leader.icon} {self.leader.name}: 协调任务中...",
            "master": f"{self.master.icon} {self.master.name}: 系统暂时无法完成深度推理。",
            "vault_saved": False,
            "superintendent_notified": False,
            "confidence": 0,
            "sample_size": 0
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
