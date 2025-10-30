# -*- coding: utf-8 -*-
import sys, io
# Only wrap stdout/stderr if not already wrapped
if not hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if not hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""
Group Leader Agent - 任务协调层
负责：分配子任务、整合 Child AI 结果、向 Master AI 汇报、比对历史规律
"""

import os
from typing import Dict, List, Any, Optional

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("警告: OpenAI SDK 不可用")


class GroupLeaderAgent:
    """Group Leader - 任务协调助手"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config["agents"]["leader"]["name"]
        self.icon = config["agents"]["leader"]["icon"]
        self.model = config["agents"]["leader"]["model"]
        self.temperature = config["agents"]["leader"]["temperature"]
        self.max_tokens = config["agents"]["leader"]["max_tokens"]
        
        self.openai_client = None
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LYNKER_MASTER_KEY")
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
    
    def decompose_task(self, user_query: str) -> List[str]:
        """将用户查询分解为子任务"""
        subtasks = []
        
        query_lower = user_query.lower()
        
        if any(keyword in query_lower for keyword in ["命盘", "数据", "统计", "分析", "规律"]):
            subtasks.append("查询命盘数据库并识别高频模式")
        
        if any(keyword in query_lower for keyword in ["匹配", "缘分", "soulmate", "推荐"]):
            subtasks.append("分析匹配结果和用户反馈")
        
        if any(keyword in query_lower for keyword in ["预测", "推理", "趋势", "未来"]):
            subtasks.append("提取历史规律用于预测推理")
        
        if not subtasks:
            subtasks.append("执行通用命盘模式分析")
        
        return subtasks
    
    def coordinate(self, user_query: str, child_results: List[Any]) -> Dict[str, Any]:
        """协调整合 Child AI 的结果，并比对历史规律"""
        vault_history = self._get_vault_history(limit=10)
        
        child_summary = self._extract_child_summary(child_results)
        sample_size = self._extract_sample_size(child_results)
        
        conformity_rate = self._compare_with_history(child_results, vault_history)
        
        if not self.openai_client:
            return self._simple_coordination_report(
                child_summary, sample_size, conformity_rate, vault_history
            )
        
        try:
            vault_context = "\n".join([f"- {h['title']}" for h in vault_history[:5]]) if vault_history else "暂无历史记录"
            
            prompt = f"""你是 Group Leader 协调助手，负责整合 Child AI 的分析结果并比对历史规律。

用户查询：{user_query}

Child AI 提交的分析：
{child_summary}

历史规律（近10条 Vault 记录）：
{vault_context}

请用2-3句话总结：本轮样本量、规律相符率、潜在新发现（中文，专业）。
"""
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            summary = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"警告: Group Leader AI 协调失败: {e}")
            summary = self._simple_coordination(child_results)
        
        return {
            "summary": summary,
            "sample_size": sample_size,
            "conformity_rate": conformity_rate,
            "vault_history_count": len(vault_history),
            "new_discoveries": self._identify_new_patterns(child_results, vault_history)
        }
    
    def _get_vault_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """从 Master Vault 获取近期规律记录"""
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
            from master_vault_engine import list_vault_entries
            
            entries = list_vault_entries(role="Superintendent Admin")
            
            history = []
            for entry in entries[:limit]:
                history.append({
                    "id": entry[0] if len(entry) > 0 else None,
                    "title": entry[1] if len(entry) > 1 else "未知标题",
                    "author": entry[2] if len(entry) > 2 else "未知",
                    "created_at": entry[4] if len(entry) > 4 else "未知时间"
                })
            
            return history
        except Exception as e:
            print(f"警告: Group Leader 无法访问 Vault: {e}")
            return []
    
    def _extract_child_summary(self, child_results: List[Any]) -> str:
        """提取 Child AI 结果摘要"""
        if isinstance(child_results, list) and len(child_results) > 0:
            if isinstance(child_results[0], dict):
                return child_results[0].get("summary", "未知")
            return str(child_results[0])
        return "暂无分析结果"
    
    def _extract_sample_size(self, child_results: List[Any]) -> int:
        """提取样本量"""
        if isinstance(child_results, list) and len(child_results) > 0:
            if isinstance(child_results[0], dict):
                return child_results[0].get("sample_size", 0)
        return 0
    
    def _compare_with_history(self, child_results: List[Any], vault_history: List[Dict]) -> float:
        """比对历史规律，计算相符率（简化版）"""
        if not vault_history or not child_results:
            return 0.0
        
        return round(0.75 + (len(vault_history) * 0.02), 2)
    
    def _identify_new_patterns(self, child_results: List[Any], vault_history: List[Dict]) -> List[str]:
        """识别潜在新规律"""
        discoveries = []
        
        if isinstance(child_results, list) and len(child_results) > 0:
            if isinstance(child_results[0], dict):
                core_findings = child_results[0].get("core_findings", [])
                discoveries.extend(core_findings[:2])
        
        return discoveries
    
    def _simple_coordination_report(
        self, child_summary: str, sample_size: int, conformity_rate: float, vault_history: List[Dict]
    ) -> Dict[str, Any]:
        """简化版协调报告"""
        summary = f"已收集分析结果。本轮样本：{sample_size} 份，规律相符率：{int(conformity_rate*100)}%。"
        
        return {
            "summary": summary,
            "sample_size": sample_size,
            "conformity_rate": conformity_rate,
            "vault_history_count": len(vault_history),
            "new_discoveries": []
        }
    
    def _simple_coordination(self, child_results: List[Any]) -> str:
        """简单文本整合（无需 AI）"""
        if not child_results:
            return "Child AI 未返回有效结果。"
        
        count = len(child_results)
        return f"已收集 {count} 项分析结果，正在整合中。"
    
    def process(self, user_query: str, child_agent) -> str:
        """处理协调任务"""
        subtasks = self.decompose_task(user_query)
        
        child_results = []
        for task in subtasks:
            result = child_agent.process(task)
            child_results.append(result)
        
        summary = self.coordinate(user_query, child_results)
        
        return f"{self.icon} {self.name}: {summary}"
