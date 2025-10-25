"""
真命盘验证器 - AI 评分引擎
使用 GPT-4o-mini 进行三维度评估，OpenAI 不可用时降级到启发式评分
评分维度：结构一致性（45%）、事件应验（35%）、人格匹配（20%）
"""
import os
import re
import json
import datetime
from typing import Dict, Any

try:
    from openai import OpenAI
    OPENAI_OK = True
except Exception:
    OPENAI_OK = False

# 评分权重配置
WEIGHTS = {
    "structure_consistency": 0.45,  # 结构一致性
    "event_alignment": 0.35,         # 事件应验一致性
    "persona_match": 0.20            # 人格断宫一致性
}

def parse_basic_fields(raw: str) -> Dict[str, Any]:
    """
    从文墨天机 TXT 格式中提取基本字段
    轻量级解析器，支持多种格式
    """
    d = {
        "name": "",
        "gender": "",
        "birth_time": "",
        "ziwei_palace": "",
        "main_star": "",
        "shen_palace": ""
    }
    
    # 提取姓名
    m = re.search(r"(?:姓名|命主|名字)\s*[:：]\s*(\S+)", raw)
    d["name"] = m.group(1) if m else ""
    
    # 提取性别
    m = re.search(r"性别\s*[:：]\s*(\S+)", raw)
    d["gender"] = m.group(1) if m else ""
    
    # 提取出生时间（支持多种格式）
    m = re.search(r"(?:鐘錶時間|出生时间|出生|生辰)\s*[:：]\s*([0-9\-\s:]+)", raw)
    if m:
        birth_str = m.group(1).replace(" ", "T")
        d["birth_time"] = birth_str
    
    # 提取命宫
    m = re.search(r"命\s*宮\[([^\]]+)\]", raw)
    d["ziwei_palace"] = m.group(1) if m else ""
    
    # 提取主星
    m = re.search(r"主星\s*[:：]\s*([^\n]+)", raw)
    if m:
        stars = m.group(1).split(",")
        d["main_star"] = stars[0].strip() if stars else ""
    
    # 提取身宫
    m = re.search(r"身宮\s*[:：]\s*(\S+)", raw)
    d["shen_palace"] = m.group(1) if m else ""
    
    return d


def offline_score(raw: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
    """
    启发式评分（当 OpenAI 不可用时）
    基于关键字段完整性和特征关键词进行评估
    修复：确保完整命盘可以达到 0.8 以上
    """
    # 结构一致性：基于关键字段完整性
    required_fields = ["gender", "birth_time", "ziwei_palace", "main_star"]
    filled_count = sum(1 for k in required_fields if parsed.get(k))
    # 修改：0.4 ~ 1.0（4个字段都填写则满分）
    structure = 0.4 + 0.15 * filled_count
    
    # 事件应验一致性：检查是否包含大限、流年等关键词
    # 修改：提高基准分和满分
    event_keywords = ["大限", "流年", "运势", "应验", "事件"]
    event_count = sum(1 for kw in event_keywords if kw in raw)
    event = 0.5 + 0.1 * min(event_count, 5)  # 0.5 ~ 1.0
    
    # 人格一致性：检查是否包含性别、身主、命主等关键词
    # 修改：提高基准分
    persona_keywords = ["性别", "身主", "命主", "命宮", "身宮", "夫妻", "财帛"]
    persona_count = sum(1 for kw in persona_keywords if kw in raw)
    persona = 0.6 + 0.08 * min(persona_count, 5)  # 0.6 ~ 1.0
    
    # 加权总分
    total = (
        structure * WEIGHTS["structure_consistency"] +
        event * WEIGHTS["event_alignment"] +
        persona * WEIGHTS["persona_match"]
    )
    
    return {
        "structure": round(structure, 3),
        "event": round(event, 3),
        "persona": round(persona, 3),
        "score": round(min(1.0, total), 3)
    }


def llm_score(raw: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
    """
    使用 GPT-4o-mini 进行 AI 评分
    如果 OpenAI 不可用，自动降级到启发式评分
    """
    if not OPENAI_OK:
        return offline_score(raw, parsed)
    
    # 尝试获取 API key
    key = os.getenv("LYNKER_MASTER_KEY") or os.getenv("OPENAI_API_KEY")
    if not key:
        return offline_score(raw, parsed)
    
    try:
        client = OpenAI(api_key=key)
        
        prompt = f"""你是一位紫微斗數驗盘審核官。
請根據以下原始文本評估是否為真命盤，並給出三個分數項（0~1之間的小數）：

1) 結構一致性（structure）：命盤格局是否完整、宮位配置是否合理
2) 事件應驗一致性（event）：是否包含可驗證的人生事件、大限流年等資訊
3) 人格斷宮一致性（persona）：性別、性格特徵是否與宮位主星相符

最後輸出 JSON 格式：{{"structure":0.0~1.0,"event":0.0~1.0,"persona":0.0~1.0}}

原始文本：
{raw[:8000]}
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        
        txt = response.choices[0].message.content
        
        # 提取 JSON
        json_match = re.search(r"\{.*\}", txt, re.S)
        if not json_match:
            return offline_score(raw, parsed)
        
        j = json.loads(json_match.group(0))
        structure = j.get("structure", 0.5)
        event = j.get("event", 0.5)
        persona = j.get("persona", 0.5)
        
    except Exception as e:
        print(f"⚠️  OpenAI 评分失败，降级到启发式评分: {str(e)}")
        return offline_score(raw, parsed)
    
    # 加权总分
    total = (
        structure * WEIGHTS["structure_consistency"] +
        event * WEIGHTS["event_alignment"] +
        persona * WEIGHTS["persona_match"]
    )
    
    return {
        "structure": round(structure, 3),
        "event": round(event, 3),
        "persona": round(persona, 3),
        "score": round(min(1.0, total), 3)
    }


def verify_raw(raw_text: str) -> Dict[str, Any]:
    """
    完整验证流程：解析 + 评分
    返回：{"parsed": {...}, "score": {...}}
    """
    parsed = parse_basic_fields(raw_text)
    score = llm_score(raw_text, parsed)
    
    return {
        "parsed": parsed,
        "score": score
    }
