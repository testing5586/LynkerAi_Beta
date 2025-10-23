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
    
    def reason(self, user_query: str, leader_report: Dict[str, Any], vault_context: Optional[str] = None) -> Dict[str, Any]:
        """执行主控推理（模式归纳 + 异常值解释）"""
        if not self.openai_client:
            return self._simple_reasoning_report(user_query, leader_report)
        
        try:
            leader_summary = leader_report.get("summary", "未知汇报") if isinstance(leader_report, dict) else str(leader_report)
            sample_size = leader_report.get("sample_size", 0) if isinstance(leader_report, dict) else 0
            conformity_rate = leader_report.get("conformity_rate", 0) if isinstance(leader_report, dict) else 0
            new_discoveries = leader_report.get("new_discoveries", []) if isinstance(leader_report, dict) else []
            
            context = f"""
用户查询：{user_query}

Group Leader 汇报：
{leader_summary}

样本量：{sample_size} 份
规律相符率：{int(conformity_rate*100)}%
新发现：{', '.join(new_discoveries) if new_discoveries else '无'}
"""
            
            if vault_context:
                context += f"\n\nMaster Vault 知识库：\n{vault_context}"
            
            context += """

请执行：
1. 模式归纳：总结命理规律的核心特征
2. 异常值解释：分析不符合规律的特殊案例
3. 与紫微飞化系统交叉验证
4. 给出可执行建议（样本扩容、权重调优等）

输出格式：自然语言结论（中文，专业）。
"""
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": context}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            conclusion = response.choices[0].message.content.strip()
            
            confidence = self._calculate_confidence(conformity_rate, sample_size)
            
            return {
                "conclusion": conclusion,
                "confidence": confidence,
                "sample_size": sample_size,
                "conformity_rate": conformity_rate,
                "new_discoveries": new_discoveries,
                "should_save_to_vault": confidence >= 0.80
            }
        except Exception as e:
            print(f"⚠️ Master AI 推理失败: {e}")
            return self._simple_reasoning_report(user_query, leader_report)
    
    def _calculate_confidence(self, conformity_rate: float, sample_size: int) -> float:
        """计算置信度（基于相符率和样本量）"""
        base_confidence = conformity_rate
        
        if sample_size >= 50:
            size_bonus = 0.10
        elif sample_size >= 20:
            size_bonus = 0.05
        else:
            size_bonus = 0.0
        
        return min(base_confidence + size_bonus, 0.95)
    
    def _simple_reasoning_report(self, user_query: str, leader_report: Any) -> Dict[str, Any]:
        """简化版推理报告"""
        if isinstance(leader_report, dict):
            summary = leader_report.get("summary", "未知")
            sample_size = leader_report.get("sample_size", 0)
            conformity_rate = leader_report.get("conformity_rate", 0)
        else:
            summary = str(leader_report)
            sample_size = 0
            conformity_rate = 0
        
        conclusion = f"基于 Group Leader 的分析，{summary}。建议进一步收集数据验证此规律。"
        confidence = self._calculate_confidence(conformity_rate, sample_size)
        
        return {
            "conclusion": conclusion,
            "confidence": confidence,
            "sample_size": sample_size,
            "conformity_rate": conformity_rate,
            "new_discoveries": [],
            "should_save_to_vault": False
        }
    
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
