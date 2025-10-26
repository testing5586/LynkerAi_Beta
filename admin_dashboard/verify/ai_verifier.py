"""
AI命盘验证器
集成OpenAI API调用Child AI进行结构化验证
"""
import os
import json
import sys
from openai import OpenAI
from .ai_prompts import get_bazi_child_ai_prompt, get_ziwei_child_ai_prompt

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # 优先使用简化版知识检索路由
    from knowledge.retrieval_router import find_relevant_knowledge as find_knowledge_simple
    from knowledge.access_control import allow_access
    KNOWLEDGE_BASE_AVAILABLE = True
    USE_SIMPLE_ROUTER = True
except ImportError:
    try:
        # 回退到完整版
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from lkk_knowledge_base.retrieval_router import find_relevant_knowledge
        KNOWLEDGE_BASE_AVAILABLE = True
        USE_SIMPLE_ROUTER = False
    except ImportError:
        print("⚠️ 知识库模块未找到，AI 验证将不使用知识库增强")
        KNOWLEDGE_BASE_AVAILABLE = False
        USE_SIMPLE_ROUTER = False

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
    
    # 构建知识库增强上下文
    knowledge_context = ""
    if KNOWLEDGE_BASE_AVAILABLE and life_events:
        try:
            query = f"{chart_type} 命盘验证 {life_events[:100]}"
            
            if USE_SIMPLE_ROUTER:
                # 使用简化版检索路由
                results = find_knowledge_simple(query)
                knowledge_parts = []
                
                for ktype, fname, content in results:
                    # Child AI 只能访问 pattern 类型（根据 access_control.py）
                    if allow_access("child", ktype):
                        if ktype == "pattern":
                            knowledge_parts.append(f"【统计规律】{fname}: {json.dumps(content, ensure_ascii=False)[:200]}...")
                
                if knowledge_parts:
                    knowledge_context = "\n".join(knowledge_parts) + "\n\n"
                    print(f"✅ Child AI 知识库增强: {len(knowledge_parts)} 条统计规律")
            else:
                # 使用完整版检索路由
                knowledge = find_relevant_knowledge(query, categories=["rules", "patterns"], max_results=3)
                knowledge_parts = []
                
                if knowledge.get("rules"):
                    knowledge_parts.append("【命理规则参考】")
                    for rule in knowledge["rules"]:
                        knowledge_parts.append(f"- {rule['content'][:200]}...")
                
                if knowledge.get("patterns"):
                    knowledge_parts.append("\n【统计规律参考】")
                    for pattern in knowledge["patterns"]:
                        pattern_data = pattern.get("content", {})
                        if isinstance(pattern_data, dict):
                            category = pattern_data.get("category", "未知")
                            count = pattern_data.get("total_count", 0)
                            knowledge_parts.append(f"- {category} 类规律（{count} 条统计）")
                        else:
                            knowledge_parts.append(f"- {pattern.get('source', '统计规律')}")
                
                if knowledge_parts:
                    knowledge_context = "\n".join(knowledge_parts) + "\n\n"
                    print(f"✅ 知识库增强已启用: {knowledge.get('summary', '匹配成功')}")
        except Exception as e:
            print(f"⚠️ 知识库查询失败: {e}")
    
    # 构建用户输入
    user_message = f"""
{knowledge_context}命盘数据：
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
