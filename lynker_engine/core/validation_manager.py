"""
LynkerAI 延迟点准机制 - Validation Manager
处理命理断语的验证按钮生成和数据记录
"""
import re
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple


def generate_statement_id(statement_text: str) -> str:
    """
    根据断语文本生成唯一的 statement_id
    例如: "太阴陷＝母缘淡" -> "TAIYIN_FALL_WEAK_PARENT"
    """
    # 简化文本，提取关键词
    simplified = re.sub(r'[^\w\u4e00-\u9fff]', '_', statement_text)
    # 转换为大写英文和拼音组合
    keywords = {
        '太阴': 'TAIYIN',
        '太阳': 'TAIYANG',
        '贪狼': 'TANLANG',
        '巨门': 'JUMEN',
        '天相': 'TIANXIANG',
        '天梁': 'TIANLIANG',
        '七杀': 'QISHA',
        '破军': 'POJUN',
        '武曲': 'WUQU',
        '廉贞': 'LIANZHEN',
        '紫微': 'ZIWEI',
        '天府': 'TIANFU',
        '太乙': 'TAIYI',
        '禄存': 'LUCUN',
        '文曲': 'WENQU',
        '左辅': 'ZUOFU',
        '右弼': 'YOUBI',
        '文昌': 'WENCHANG',
        '天机': 'TIANJI',
        '火星': 'HUOXING',
        '铃星': 'LINGXING',
        '地劫': 'DIJIE',
        '地空': 'DIKONG',
        '陷': 'FALL',
        '庙': 'TEMPLE',
        '旺': 'STRONG',
        '得': 'GET',
        '失': 'LOSE',
        '母': 'MOTHER',
        '父': 'FATHER',
        '缘': 'RELATION',
        '淡': 'WEAK',
        '浓': 'STRONG',
        '事业': 'CAREER',
        '婚姻': 'MARRIAGE',
        '财运': 'WEALTH',
        '健康': 'HEALTH',
        '子女': 'CHILDREN'
    }
    
    # 替换关键词
    for chinese, english in keywords.items():
        simplified = simplified.replace(chinese, english)
    
    # 清理并生成ID
    simplified = re.sub(r'_+', '_', simplified).strip('_')
    return simplified[:50] if len(simplified) > 50 else simplified


def is_fortune_statement(text: str) -> bool:
    """
    检测文本是否包含命理断语
    """
    statement_indicators = ['＝', '→', '显示', '代表', '象征', '意味着', '表示', '预示', '暗示']
    return any(indicator in text for indicator in statement_indicators)


def append_truth_buttons(ai_text: str, statement_id: Optional[str] = None) -> str:
    """
    在AI输出的命理断语后附加验证按钮
    
    Args:
        ai_text: AI输出的文本
        statement_id: 可选的预生成statement_id，如果不提供则自动生成
    
    Returns:
        带有验证按钮的文本
    """
    if not is_fortune_statement(ai_text):
        return ai_text
    
    # 如果没有提供statement_id，则生成一个
    if not statement_id:
        statement_id = generate_statement_id(ai_text)
    
    # 添加验证按钮
    buttons_text = f"\n\n👉 这句准吗？ [✅ 准](#yes-{statement_id}) [❌ 不准](#no-{statement_id})"
    
    return ai_text + buttons_text


def extract_statements_from_text(text: str) -> List[Tuple[str, str]]:
    """
    从文本中提取所有命理断语及其对应的statement_id
    
    Returns:
        List of (statement_text, statement_id) tuples
    """
    statements = []
    lines = text.split('\n')
    
    for line in lines:
        if is_fortune_statement(line.strip()):
            statement_id = generate_statement_id(line.strip())
            statements.append((line.strip(), statement_id))
    
    return statements


def format_ai_response(text: str, chart_locked: bool, statement_id: Optional[str] = None) -> str:
    """
    格式化AI响应，根据是否锁定命盘决定是否添加验证按钮
    
    Args:
        text: AI原始响应文本
        chart_locked: 是否已锁定真命盘
        statement_id: 可选的statement_id
    
    Returns:
        格式化后的响应文本
    """
    if not chart_locked:
        return text
    
    return append_truth_buttons(text, statement_id)


def parse_validation_click(click_data: str) -> Dict:
    """
    解析用户点击验证按钮的数据
    
    Args:
        click_data: 格式为 "#yes-STATEMENT_ID" 或 "#no-STATEMENT_ID"
    
    Returns:
        包含解析结果的字典
    """
    if not click_data.startswith('#'):
        return {"error": "Invalid click data format"}
    
    parts = click_data[1:].split('-', 1)  # 移除#并分割
    if len(parts) != 2:
        return {"error": "Invalid click data format"}
    
    action, statement_id = parts
    
    return {
        "user_choice": action == "yes",
        "statement_id": statement_id,
        "valid": True
    }


def create_validation_log(user_id: str, chart_id: str, statement_id: str, 
                        ai_statement: str, user_choice: bool, 
                        source_ai: str = "Primary", phase: str = "final_validation",
                        trust_score: float = 0.0) -> Dict:
    """
    创建验证日志数据结构
    
    Args:
        user_id: 用户ID
        chart_id: 命盘ID
        statement_id: 断语ID
        ai_statement: AI断语文本
        user_choice: 用户选择（True=准，False=不准）
        source_ai: AI来源
        phase: 验证阶段
        trust_score: 信任分数
    
    Returns:
        验证日志字典
    """
    return {
        "user_id": user_id,
        "chart_id": chart_id,
        "statement_id": statement_id,
        "ai_statement": ai_statement,
        "user_choice": user_choice,
        "ai_prediction": True,  # AI默认认为自己的断语是准确的
        "match_result": user_choice,  # 如果用户选择"准"则匹配成功
        "phase": phase,
        "timestamp": datetime.now().isoformat(),
        "trust_score": trust_score,
        "source_ai": source_ai
    }


# 预定义的常见断语模板
COMMON_STATEMENTS = {
    "TAIYIN_FALL_WEAK_PARENT": "太阴陷＝母缘淡",
    "TANLANG_IN_WEALTH_GOOD": "贪狼入财宫＝财运佳",
    "QISHA_IN_CAREER_STRONG": "七杀坐官禄＝事业心强",
    "POJUN_IN_MARRIAGE_UNSTABLE": "破军入夫妻＝婚姻多变",
    "ZIWEI_IN_SELF_HIGH_STATUS": "紫微坐命＝地位高"
}


def get_predefined_statement(statement_id: str) -> Optional[str]:
    """
    获取预定义的断语文本
    
    Args:
        statement_id: 断语ID
    
    Returns:
        断语文本，如果不存在则返回None
    """
    return COMMON_STATEMENTS.get(statement_id)