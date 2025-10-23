"""
Master AI Agent - 主控推理层
负责：综合分析命盘、Vault知识、用户反馈，提供最终结论
"""

import os
from typing import Dict, Any, Optional

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI SDK 不可用")


class MasterAgent:
    """Master AI - 主控推理助手"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config["agents"]["master"]["name"]
        self.icon = config["agents"]["master"]["icon"]
        self.model = config["agents"]["master"]["model"]
        self.temperature = config["agents"]["master"]["temperature"]
        self.max_tokens = config["agents"]["master"]["max_tokens"]
        
        self.openai_client = None
        if OPENAI_AVAILABLE:
            api_key = os.getenv("LYNKER_MASTER_KEY") or os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
        
        self.system_prompt = """你是 LynkerAI 的 Master AI（主控推理中枢），负责：

1. **综合分析**：整合 Group Leader 汇报、命盘数据、Vault 知识
2. **深度推理**：发现命理规律、预测趋势、解答用户疑问
3. **决策制定**：提供最终结论和建议

你的回答应该：
- 专业且易懂（使用命理术语但加以解释）
- 基于数据和统计规律
- 提供可执行的建议
- 保持中文输出
"""
    
    def reason(self, user_query: str, leader_report: str, vault_context: Optional[str] = None) -> str:
        """执行主控推理"""
        if not self.openai_client:
            return self._simple_reasoning(user_query, leader_report)
        
        try:
            context = f"""
用户查询：{user_query}

Group Leader 汇报：
{leader_report}
"""
            
            if vault_context:
                context += f"\n\nMaster Vault 知识库：\n{vault_context}"
            
            context += "\n\n请基于以上信息提供深度分析和最终结论。"
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": context}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ Master AI 推理失败: {e}")
            return self._simple_reasoning(user_query, leader_report)
    
    def _simple_reasoning(self, user_query: str, leader_report: str) -> str:
        """简单推理（无需 AI）"""
        return f"基于 Group Leader 的分析，我认为：{leader_report}。建议进一步收集数据验证此规律。"
    
    def synthesize_knowledge(self, findings: Dict[str, Any]) -> str:
        """综合知识并决定是否存入 Vault"""
        confidence = findings.get("confidence", 0)
        
        if confidence >= self.config["vault"]["auto_encrypt_threshold"]:
            return f"此发现具有高置信度 ({confidence:.2f})，建议存入 Master Vault 加密知识库。"
        else:
            return f"此发现置信度较低 ({confidence:.2f})，建议继续观察验证。"
    
    def process(self, user_query: str, leader_report: str, vault_context: Optional[str] = None) -> str:
        """处理主控推理任务"""
        reasoning = self.reason(user_query, leader_report, vault_context)
        
        return f"{self.icon} {self.name}: {reasoning}"
