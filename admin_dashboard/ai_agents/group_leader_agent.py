"""
Group Leader Agent - 任务协调层
负责：分配子任务、整合 Child AI 结果、向 Master AI 汇报
"""

import os
from typing import Dict, List, Any

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI SDK 不可用")


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
            api_key = os.getenv("LYNKER_MASTER_KEY") or os.getenv("OPENAI_API_KEY")
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
    
    def coordinate(self, user_query: str, child_results: List[str]) -> str:
        """协调整合 Child AI 的结果"""
        if not self.openai_client:
            return self._simple_coordination(child_results)
        
        try:
            child_summary = "\n".join([f"- {r}" for r in child_results])
            
            prompt = f"""你是 Group Leader 协调助手，负责整合 Child AI 的分析结果。

用户查询：{user_query}

Child AI 提交的分析：
{child_summary}

请用2-3句话总结关键发现，为 Master AI 提供清晰的汇报（中文，专业）。
"""
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ Group Leader 协调失败: {e}")
            return self._simple_coordination(child_results)
    
    def _simple_coordination(self, child_results: List[str]) -> str:
        """简单文本整合（无需 AI）"""
        if not child_results:
            return "Child AI 未返回有效结果。"
        
        return f"已收集 {len(child_results)} 项分析结果：" + "；".join(child_results[:2])
    
    def process(self, user_query: str, child_agent) -> str:
        """处理协调任务"""
        subtasks = self.decompose_task(user_query)
        
        child_results = []
        for task in subtasks:
            result = child_agent.process(task)
            child_results.append(result)
        
        summary = self.coordinate(user_query, child_results)
        
        return f"{self.icon} {self.name}: {summary}"
