"""
评分引擎 - 智能匹配算法
权重分配：事件45% + 性格30% + 婚姻15% + 健康10%
"""
import re
from typing import Dict, List, Any


# 评分权重配置
WEIGHTS = {
    "events": 0.45,     # 重大事件命中
    "traits": 0.30,     # 性格特质匹配
    "marriage": 0.15,   # 婚姻状况
    "health": 0.10      # 健康记录
}


def extract_life_events(wizard: Dict[str, Any]) -> List[str]:
    """从 Wizard 问答中提取生命事件关键词"""
    events = []
    
    # 家庭事件
    if wizard.get("family"):
        events.extend(["父母", "兄弟", "姐妹"])
    
    # 学业事件
    if wizard.get("education"):
        edu = wizard["education"]
        if "留学" in str(edu):
            events.append("留学")
        if "硕士" in str(edu) or "博士" in str(edu):
            events.append("高学历")
    
    # 事业事件
    if wizard.get("career"):
        career = wizard["career"]
        if "创业" in str(career):
            events.append("创业")
        if "转行" in str(career):
            events.append("转行")
        if "失业" in str(career):
            events.append("失业")
    
    # 婚姻事件
    if wizard.get("marriage"):
        marriage = wizard["marriage"]
        if "离婚" in str(marriage):
            events.append("离婚")
        if "再婚" in str(marriage):
            events.append("再婚")
        if "未婚" in str(marriage):
            events.append("未婚")
    
    # 财务事件
    if wizard.get("finance"):
        finance = wizard["finance"]
        if "破产" in str(finance):
            events.append("破产")
        if "发财" in str(finance) or "致富" in str(finance):
            events.append("发财")
    
    # 健康事件
    if wizard.get("health"):
        health = wizard["health"]
        if "手术" in str(health):
            events.append("手术")
        if "重病" in str(health):
            events.append("重病")
    
    # 重大事件
    if wizard.get("major_events"):
        events.extend(str(wizard["major_events"]).split(","))
    
    return [e.strip() for e in events if e.strip()]


def match_event_score(events: List[str], parsed: Dict[str, Any]) -> float:
    """
    事件命中评分
    匹配 Wizard 事件 与 命盘解析内容
    """
    if not events:
        return 0.5  # 无事件信息，给中等分
    
    birth_data_str = str(parsed.get("birth_data", ""))
    main_star = parsed.get("main_star", "")
    
    matched_count = 0
    total_count = len(events)
    
    for event in events:
        if event in birth_data_str or event in main_star:
            matched_count += 1
    
    return matched_count / total_count if total_count > 0 else 0.5


def match_traits_score(wizard: Dict[str, Any], parsed: Dict[str, Any]) -> float:
    """
    性格特质评分
    基于命宫主星与性格描述的匹配度
    """
    main_star = parsed.get("main_star", "")
    
    # 简单启发式：某些主星对应特定性格
    score = 0.5
    
    if "紫微" in main_star:
        score += 0.2
    if "天府" in main_star:
        score += 0.15
    if "廉贞" in main_star:
        score += 0.1
    
    return min(1.0, score)


def match_marriage_score(wizard: Dict[str, Any], parsed: Dict[str, Any]) -> float:
    """
    婚姻状况评分
    """
    marriage_info = wizard.get("marriage", "")
    
    # 简单匹配逻辑
    if "离婚" in str(marriage_info):
        return 0.7
    if "未婚" in str(marriage_info):
        return 0.6
    
    return 0.5


def match_health_score(wizard: Dict[str, Any], parsed: Dict[str, Any]) -> float:
    """
    健康记录评分
    """
    health_info = wizard.get("health", "")
    
    if "手术" in str(health_info) or "重病" in str(health_info):
        return 0.75
    
    return 0.5


def score_match(parsed: Dict[str, Any], wizard: Dict[str, Any], notes: str = "") -> Dict[str, Any]:
    """
    核心评分函数
    
    Args:
        parsed: 解析的命盘数据
        wizard: Wizard 问答结果
        notes: 手写补充内容
    
    Returns:
        {
            "score": 0.0-1.0,
            "weights": {...},
            "signals": [{key, value, weight}, ...],
            "candidates": [{id, label, score, explain}, ...]
        }
    """
    events = extract_life_events(wizard)
    
    # 计算各维度分数
    events_score = match_event_score(events, parsed)
    traits_score = match_traits_score(wizard, parsed)
    marriage_score = match_marriage_score(wizard, parsed)
    health_score = match_health_score(wizard, parsed)
    
    # 加权总分
    total_score = (
        events_score * WEIGHTS["events"] +
        traits_score * WEIGHTS["traits"] +
        marriage_score * WEIGHTS["marriage"] +
        health_score * WEIGHTS["health"]
    )
    
    # 生成信号详情
    signals = [
        {"key": "重大事件命中", "value": events_score >= 0.6, "weight": 0.18},
        {"key": "性格特质匹配", "value": traits_score >= 0.6, "weight": 0.12},
        {"key": "婚姻状况一致", "value": marriage_score >= 0.6, "weight": 0.08},
        {"key": "健康记录匹配", "value": health_score >= 0.5, "weight": 0.05}
    ]
    
    # 生成候选命盘（这里简化处理，实际应查询数据库）
    candidates = [
        {
            "id": None,
            "label": f"{parsed.get('name', '未知')} ({parsed.get('birth_time', '时辰待定')})",
            "score": round(total_score, 3),
            "explain": f"事件命中度 {events_score:.2f}，性格匹配度 {traits_score:.2f}"
        }
    ]
    
    return {
        "score": round(total_score, 3),
        "weights": WEIGHTS,
        "signals": signals,
        "candidates": candidates
    }
