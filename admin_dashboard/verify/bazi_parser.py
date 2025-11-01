"""
八字数据智能解析器
Intelligent Bazi Chart Parser

核心功能：
1. 容错解析多种八字格式（四柱、文墨天机、自定义表格）
2. 智能判断数据完整度（has_details）
3. 区分"只有四柱"vs"包含十神/神煞/藏干"的完整命盘
"""

import re

# 四柱关键字
FOUR_PILLAR_KEYS = ["年柱", "月柱", "日柱", "时柱"]

# 命理细节关键字（判断是否为完整命盘）
DETAIL_KEYWORDS = [
    "正财", "偏财", "食神", "伤官", "七杀", "正官",
    "比肩", "劫财", "正印", "偏印", 
    "藏干", "神煞", "纳音", "大运", "流年",
    "地支藏干", "旺衰", "用神", "喜神", "忌神",
    "长生", "沐浴", "冠带", "临官", "帝旺", "衰", "病", "死", "墓", "绝", "胎", "养"
]


def parse_bazi_text(raw: str) -> dict:
    """
    超容错八字文本解析器
    
    支持格式：
    1. 文墨天机简洁版："年柱:庚辰 月柱:己卯 日柱:丙戌 时柱:己丑"
    2. 完整版：包含十神、神煞、藏干、纳音等详细信息
    3. JSON 对象格式
    
    Args:
        raw: 原始八字文本或 JSON 字符串
    
    Returns:
        dict: {
            "year_pillar": "庚辰",
            "month_pillar": "己卯",
            "day_pillar": "丙戌",
            "hour_pillar": "己丑",
            "birth_datetime": "2000-03-20 08:18",
            "raw": "原始文本",
            "has_details": True/False,  # 🔥 关键字段
            "format_type": "simple" | "detailed"
        }
    """
    text = (raw or "").strip()
    
    # 处理 JSON 格式输入
    if text.startswith("{") and text.endswith("}"):
        try:
            import json
            data = json.loads(text)
            # 如果已经是 JSON，提取字段
            result = {
                "year_pillar": data.get("year_pillar", ""),
                "month_pillar": data.get("month_pillar", ""),
                "day_pillar": data.get("day_pillar", ""),
                "hour_pillar": data.get("hour_pillar", ""),
                "birth_datetime": data.get("birth_datetime", "") or data.get("birth_date", ""),
                "raw": raw,
                "has_details": data.get("has_details", False),
                "format_type": "json"
            }
            return result
        except:
            pass
    
    # 标准化文本（全角→半角，多种分隔符统一）
    text = text.replace("：", ":").replace("　", " ").replace("\r\n", "\n")
    text = text.replace("\t", " ")
    
    result = {
        "year_pillar": "",
        "month_pillar": "",
        "day_pillar": "",
        "hour_pillar": "",
        "birth_datetime": "",
        "raw": raw,
        "has_details": False,
        "format_type": "unknown"
    }
    
    # ========== 步骤1：提取四柱 ==========
    # 🔧 优先检测单行格式（最常见）："年柱:庚辰 月柱:己卯 日柱:丙戌 时柱:己丑"
    pillars_in_text = re.findall(r"(年柱|月柱|日柱|时柱)\s*[:：]?\s*([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])", text)
    
    if pillars_in_text:
        # 找到四柱数据，批量提取
        for key, val in pillars_in_text:
            if key == "年柱":
                result["year_pillar"] = val
            elif key == "月柱":
                result["month_pillar"] = val
            elif key == "日柱":
                result["day_pillar"] = val
            elif key == "时柱":
                result["hour_pillar"] = val
    
    # 🔧 兼容多行格式（备用方案）
    if not result["year_pillar"]:
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue
            
            m = re.match(r"^(年柱|月柱|日柱|时柱)\s*[:：]?\s*([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])", line)
            if m:
                key = m.group(1)
                val = m.group(2).strip()
                
                if key == "年柱":
                    result["year_pillar"] = val
                elif key == "月柱":
                    result["month_pillar"] = val
                elif key == "日柱":
                    result["day_pillar"] = val
                elif key == "时柱":
                    result["hour_pillar"] = val
    
    # ========== 步骤2：提取出生时间 ==========
    for line in text.split("\n"):
        line = line.strip()
        if "出生时间" in line or "出生日期" in line or "阳历" in line or "公历" in line:
            # 提取日期时间
            date_match = re.search(r"(\d{4})[-年/\.](\d{1,2})[-月/\.](\d{1,2})", line)
            time_match = re.search(r"(\d{1,2}):(\d{2})", line)
            
            if date_match:
                year = date_match.group(1)
                month = date_match.group(2).zfill(2)
                day = date_match.group(3).zfill(2)
                time_str = ""
                if time_match:
                    hour = time_match.group(1).zfill(2)
                    minute = time_match.group(2)
                    time_str = f" {hour}:{minute}"
                result["birth_datetime"] = f"{year}-{month}-{day}{time_str}"
    
    # ========== 步骤2：判断数据完整度 ==========
    # 2.1 检查是否包含命理细节关键字
    has_detail_keywords = any(kw in text for kw in DETAIL_KEYWORDS)
    
    # 2.2 检查四柱是否齐全
    four_pillars_complete = all([
        result["year_pillar"],
        result["month_pillar"],
        result["day_pillar"],
        result["hour_pillar"]
    ])
    
    # 2.3 判断格式类型
    if has_detail_keywords:
        result["format_type"] = "detailed"  # 完整命盘
        result["has_details"] = True
    elif four_pillars_complete:
        result["format_type"] = "simple"    # 只有四柱
        result["has_details"] = False
    else:
        result["format_type"] = "incomplete"  # 不完整
        result["has_details"] = False
    
    return result


def is_bazi_incomplete(bazi_parsed: dict) -> bool:
    """
    判断八字数据是否不完整（需要触发预言验证）
    
    Args:
        bazi_parsed: parse_bazi_text() 返回的结果
    
    Returns:
        bool: True=不完整，需要预言验证；False=完整，可以进行AI分析
    """
    return not bazi_parsed.get("has_details", False)


def get_bazi_status_message(bazi_parsed: dict) -> str:
    """
    获取八字数据状态说明
    
    Args:
        bazi_parsed: parse_bazi_text() 返回的结果
    
    Returns:
        str: 状态说明文本
    """
    format_type = bazi_parsed.get("format_type", "unknown")
    
    if format_type == "detailed":
        return "✅ 八字命盘数据完整，包含十神、神煞等详细信息，可以进行深度AI验证。"
    elif format_type == "simple":
        return "⚠️ 八字命盘只有四柱（年月日时），缺少十神、藏干、神煞等可验证的命理细节，建议通过预言验证方式进行反馈。"
    else:
        return "❌ 八字命盘数据不完整，请补充完整的四柱信息。"


# ========== 测试函数 ==========
if __name__ == "__main__":
    # 测试用例1：文墨天机简洁版（只有四柱）
    test1 = """
    年柱:庚辰
    月柱:己卯
    日柱:丙戌
    时柱:己丑
    """
    result1 = parse_bazi_text(test1)
    print("测试1 - 简洁版四柱:")
    print(f"  has_details: {result1['has_details']}")  # 应该是 False
    print(f"  format_type: {result1['format_type']}")  # 应该是 simple
    print(f"  状态: {get_bazi_status_message(result1)}")
    print()
    
    # 测试用例2：完整版（包含十神）
    test2 = """
    年柱:庚辰 正财
    月柱:己卯 伤官
    日柱:丙戌 日主
    时柱:己丑 伤官
    藏干：戊乙癸
    神煞：天德贵人、月德贵人
    """
    result2 = parse_bazi_text(test2)
    print("测试2 - 完整版:")
    print(f"  has_details: {result2['has_details']}")  # 应该是 True
    print(f"  format_type: {result2['format_type']}")  # 应该是 detailed
    print(f"  状态: {get_bazi_status_message(result2)}")
