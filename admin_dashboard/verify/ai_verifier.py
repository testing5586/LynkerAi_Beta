"""
AI命盘验证器
集成OpenAI API调用Child AI进行结构化验证
"""
import os
import json
from openai import OpenAI
from .ai_prompts import get_bazi_child_ai_prompt, get_ziwei_child_ai_prompt

# 初始化OpenAI客户端
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or os.getenv("LYNKER_MASTER_KEY"))


async def verify_chart_with_ai(chart_data: dict, life_events: str, chart_type: str, ai_name: str = None):
    """
    使用AI验证命盘
    
    参数:
        chart_data: 解析后的命盘数据
        life_events: 用户讲述的人生事件
        chart_type: 'bazi' 或 'ziwei'
        ai_name: AI名字（可选）
    
    返回:
        {
            "score": float,
            "key_matches": list,
            "key_mismatches": list,
            "notes": str
        }
    """
    # 获取对应的AI Prompt
    if chart_type == "bazi":
        system_prompt = get_bazi_child_ai_prompt(ai_name or "八字观察员")
    elif chart_type == "ziwei":
        system_prompt = get_ziwei_child_ai_prompt(ai_name or "星盘参谋")
    else:
        raise ValueError(f"不支持的命盘类型: {chart_type}")
    
    # 构建用户输入
    user_message = f"""
命盘数据：
{json.dumps(chart_data, ensure_ascii=False, indent=2)}

用户人生事件描述：
{life_events if life_events else "（暂无人生事件描述）"}

请根据以上信息，评估命盘与人生事件的匹配度，输出JSON格式的验证结果。
"""
    
    try:
        # 调用OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 使用更经济的模型
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,  # 降低随机性，确保输出稳定
            max_tokens=800
        )
        
        # 解析AI返回的JSON
        ai_output = response.choices[0].message.content.strip()
        
        # 尝试解析JSON
        result = json.loads(ai_output)
        
        # 验证必需字段
        required_fields = ["score", "key_matches", "key_mismatches", "notes"]
        for field in required_fields:
            if field not in result:
                raise ValueError(f"AI返回缺少必需字段: {field}")
        
        # 验证数据类型
        if not isinstance(result["score"], (int, float)) or not (0 <= result["score"] <= 1):
            result["score"] = 0.0
        
        if not isinstance(result["key_matches"], list):
            result["key_matches"] = []
        
        if not isinstance(result["key_mismatches"], list):
            result["key_mismatches"] = []
        
        if not isinstance(result["notes"], str):
            result["notes"] = ""
        
        return result
    
    except json.JSONDecodeError as e:
        print(f"❌ AI返回的JSON解析失败: {e}")
        print(f"AI原始输出: {ai_output}")
        # 返回默认结果
        return {
            "score": 0.0,
            "key_matches": [],
            "key_mismatches": ["AI返回格式错误，无法解析"],
            "notes": "验证失败，AI返回数据格式不正确"
        }
    
    except Exception as e:
        print(f"❌ AI验证失败: {e}")
        return {
            "score": 0.0,
            "key_matches": [],
            "key_mismatches": [f"验证过程出错: {str(e)}"],
            "notes": "系统错误，请稍后重试"
        }


def verify_chart_without_ai(chart_data: dict):
    """
    降级方案：不使用AI时的简单验证
    基于规则的基础评分
    """
    score = 0.0
    key_matches = []
    key_mismatches = []
    
    # 基础完整性检查
    if chart_data.get("name"):
        score += 0.2
        key_matches.append("命盘包含姓名信息")
    else:
        key_mismatches.append("命盘缺少姓名信息")
    
    if chart_data.get("birth_time"):
        score += 0.3
        key_matches.append("命盘包含出生时间")
    else:
        key_mismatches.append("命盘缺少出生时间")
    
    if chart_data.get("gender"):
        score += 0.1
        key_matches.append("命盘包含性别信息")
    
    # 命盘特有字段检查
    if chart_data.get("main_star") or chart_data.get("bazi_pillars"):
        score += 0.4
        key_matches.append("命盘数据结构完整")
    else:
        score = max(score - 0.2, 0.0)
        key_mismatches.append("命盘核心数据缺失")
    
    notes = f"基于规则的基础验证，综合评分 {score:.2f}（满分1.0）"
    
    return {
        "score": min(score, 1.0),
        "key_matches": key_matches,
        "key_mismatches": key_mismatches,
        "notes": notes
    }
