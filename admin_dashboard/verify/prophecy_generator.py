"""
Prophecy Generator - 命盘自动预言问题生成器
根据紫微命盘与八字结构自动生成精准预测问题

功能：
1. 解析文墨天机紫微命盘文本
2. 识别特定星曜组合与宫位配置
3. 自动生成可验证的人生预言问题
4. 支持多维度命理规则（兄弟宫、财帛宫、夫妻宫等）
"""

import re
import random
import json
from typing import List, Dict, Any


def generate_prophecies(ziwei_text: str, bazi_text: str = "") -> List[Dict[str, Any]]:
    """
    根据紫微命盘生成预言问题
    
    Args:
        ziwei_text: 文墨天机紫微命盘文本
        bazi_text: 八字命盘文本（可选，用于交叉验证）
    
    Returns:
        List[Dict]: 预言问题列表
        [
            {
                "palace": "兄弟宫",
                "question": "你兄弟宫擎羊破军，是否被兄弟姐妹连累或发生意外进院开刀？",
                "pattern": "破军+擎羊",
                "confidence": "high"
            }
        ]
    """
    prophecies = []
    
    # ========== 规则 1: 兄弟宫破军擎羊 ==========
    if re.search(r"兄弟[宮宫].*破[軍军]", ziwei_text) and re.search(r"兄弟[宮宫].*擎羊", ziwei_text):
        prophecies.append({
            "palace": "兄弟宫",
            "question": "你兄弟宫有破军擎羊，是否曾被兄弟姐妹连累或发生意外进院开刀？",
            "pattern": "破军+擎羊",
            "confidence": "high"
        })
    
    # ========== 规则 2: 财帛宫禄忌同宫 ==========
    if re.search(r"[财財][帛宮宫].*禄", ziwei_text) and re.search(r"[财財][帛宮宫].*忌", ziwei_text):
        prophecies.append({
            "palace": "财帛宫",
            "question": "你的财帛宫禄忌同宫，是否曾因信任他人投资而破财？",
            "pattern": "禄忌同宫",
            "confidence": "high"
        })
    
    # ========== 规则 3: 夫妻宫化忌 ==========
    if re.search(r"夫妻[宮宫].*[化忌|忌星]", ziwei_text):
        prophecies.append({
            "palace": "夫妻宫",
            "question": "夫妻宫有化忌，是否经历过突发的感情破裂或离异？",
            "pattern": "化忌",
            "confidence": "medium"
        })
    
    # ========== 规则 4: 疾厄宫火铃并临 ==========
    if re.search(r"疾[厄宮宫].*火星", ziwei_text) and re.search(r"疾[厄宮宫].*[鈴铃]星", ziwei_text):
        prophecies.append({
            "palace": "疾厄宫",
            "question": "疾厄宫火铃并临，是否有过开刀手术或烧伤事故？",
            "pattern": "火星+铃星",
            "confidence": "high"
        })
    
    # ========== 规则 5: 迁移宫天马 ==========
    if re.search(r"[迁遷]移[宮宫].*天[馬马]", ziwei_text):
        prophecies.append({
            "palace": "迁移宫",
            "question": "迁移宫有天马星，是否常年奔波各地或有海外发展经历？",
            "pattern": "天马",
            "confidence": "medium"
        })
    
    # ========== 规则 6: 父母宫天刑 ==========
    if re.search(r"父母[宮宫].*天刑", ziwei_text):
        prophecies.append({
            "palace": "父母宫",
            "question": "父母宫有天刑，是否父母其中一人有过法律纠纷或健康问题？",
            "pattern": "天刑",
            "confidence": "medium"
        })
    
    # ========== 规则 7: 子女宫空劫 ==========
    if re.search(r"子女[宮宫].*[空劫|地空|地劫]", ziwei_text):
        prophecies.append({
            "palace": "子女宫",
            "question": "子女宫有空劫，是否怀孕困难或子女关系疏远？",
            "pattern": "空劫",
            "confidence": "low"
        })
    
    # ========== 规则 8: 命宫紫微天府 ==========
    if re.search(r"命[宮宫].*紫微", ziwei_text) and re.search(r"命[宮宫].*天府", ziwei_text):
        prophecies.append({
            "palace": "命宫",
            "question": "你命宫紫微天府，是否从小家境优渥或有贵人相助？",
            "pattern": "紫微+天府",
            "confidence": "high"
        })
    
    # ========== 规则 9: 事业宫武曲贪狼 ==========
    if re.search(r"[事業业][宮宫].*武曲", ziwei_text) and re.search(r"[事業业][宮宫].*[貪贪]狼", ziwei_text):
        prophecies.append({
            "palace": "事业宫",
            "question": "事业宫武曲贪狼，是否从事金融、销售或高风险高回报行业？",
            "pattern": "武曲+贪狼",
            "confidence": "medium"
        })
    
    # ========== 规则 10: 福德宫廉贞 ==========
    if re.search(r"福[德宮宫].*[廉貞贞]", ziwei_text):
        prophecies.append({
            "palace": "福德宫",
            "question": "福德宫有廉贞，是否内心常有矛盾或精神压力较大？",
            "pattern": "廉贞",
            "confidence": "low"
        })
    
    # ========== 兜底规则：命盘起伏 ==========
    if not prophecies:
        prophecies.append({
            "palace": "综合",
            "question": "命盘显示你一生起伏较大，是否曾经历多次重大人生转折？",
            "pattern": "通用",
            "confidence": "low"
        })
    
    # 随机打乱顺序（避免规则顺序被识别）
    random.shuffle(prophecies)
    
    # 限制数量（避免问题过多）
    return prophecies[:6]


def analyze_prophecy_accuracy(feedback_records: List[Dict]) -> Dict[str, Any]:
    """
    分析预言准确率统计
    
    Args:
        feedback_records: 用户反馈记录列表
    
    Returns:
        Dict: 统计数据
        {
            "total": 100,
            "correct": 85,
            "accuracy": 85.0,
            "by_palace": {"兄弟宫": 0.9, "财帛宫": 0.8},
            "by_pattern": {"破军+擎羊": 0.95}
        }
    """
    if not feedback_records:
        return {
            "total": 0,
            "correct": 0,
            "accuracy": 0.0,
            "by_palace": {},
            "by_pattern": {}
        }
    
    total = len(feedback_records)
    correct = sum(1 for r in feedback_records if r.get("result") == "准")
    
    # 按宫位统计
    palace_stats = {}
    for record in feedback_records:
        palace = record.get("palace", "未知")
        if palace not in palace_stats:
            palace_stats[palace] = {"total": 0, "correct": 0}
        palace_stats[palace]["total"] += 1
        if record.get("result") == "准":
            palace_stats[palace]["correct"] += 1
    
    palace_accuracy = {
        p: round(stats["correct"] / stats["total"], 2) if stats["total"] > 0 else 0
        for p, stats in palace_stats.items()
    }
    
    return {
        "total": total,
        "correct": correct,
        "accuracy": round(correct / total * 100, 2) if total > 0 else 0,
        "by_palace": palace_accuracy
    }
