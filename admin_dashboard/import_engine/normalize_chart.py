"""
命盘数据规范化器
Chart Data Normalizer - 统一不同来源的命盘数据格式
"""

REQUIRED_KEYS = ["marriage_palace_star", "wealth_palace_star", "transformations"]

def _safe_get(d, *path, default=None):
    """安全获取嵌套字典值"""
    cur = d
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return default
        cur = cur[p]
    return cur

def normalize_from_wenmote(json_obj):
    """
    文墨天机导出 JSON → 标准结构
    期望最少字段:
      - name, gender ('男'/'女'), birth_time (ISO8601)
      - 命盘结构里能找到：夫妻宫主星 / 财帛宫主星 / 飞化信息（化禄/化忌）
    """
    name = json_obj.get("name") or json_obj.get("姓名") or "未知"
    gender = json_obj.get("gender") or json_obj.get("性别") or "未知"
    birth_time = json_obj.get("birth_time") or json_obj.get("出生时间") or None

    # 宫位 → 主星 映射（不同导出会有不同键名，这里尽量兜底）
    palace_map = json_obj.get("palaces") or json_obj.get("宫位") or {}
    
    def get_star_for(palace_key_candidates):
        for k in palace_key_candidates:
            v = palace_map.get(k)
            if isinstance(v, dict) and v.get("main_star"):
                return v["main_star"]
            if isinstance(v, str):
                return v
        return None

    marriage_star = get_star_for(["夫妻宫", "鹖尾", "Spouse", "marriage"])
    wealth_star = get_star_for(["财帛宫", "Treasury", "Wealth", "money"])

    # 飞化
    tf = json_obj.get("transformations") or {}
    hualu = bool(tf.get("hualu") or tf.get("化禄"))
    huaji = bool(tf.get("huaji") or tf.get("化忌"))

    birth_data = {
        "marriage_palace_star": marriage_star,
        "wealth_palace_star": wealth_star,
        "transformations": {
            "hualu": hualu,
            "huaji": huaji
        }
    }
    
    return {
        "name": name,
        "gender": gender,
        "birth_time": birth_time,
        "birth_data": birth_data
    }

def normalize_from_ocr(ocr_result):
    """
    OCR/TXT/DOC 粗解析 → 人工确认后写入
    高容忍度设计：缺失字段自动使用友好默认值，永不报错
    ocr_result建议提供：name, gender, birth_time, marriage_palace_star, wealth_palace_star,
                        transformations: {hualu: bool, huaji: bool}
    """
    # 姓名：默认"未命名"
    name = ocr_result.get("name") or "未命名"
    if isinstance(name, str):
        name = name.strip() or "未命名"
    
    # 性别：默认"未知"
    gender = ocr_result.get("gender") or "未知"
    if isinstance(gender, str):
        gender = gender.strip() or "未知"
    
    # 出生时间：空字符串转为 None（数据库兼容）
    birth_time = ocr_result.get("birth_time")
    if birth_time and isinstance(birth_time, str):
        birth_time = birth_time.strip() or None  # 空字符串 → None
    else:
        birth_time = None
    
    # 宫位主星：允许 None
    marriage_star = ocr_result.get("marriage_palace_star")
    if marriage_star and isinstance(marriage_star, str):
        marriage_star = marriage_star.strip() or None
    
    wealth_star = ocr_result.get("wealth_palace_star")
    if wealth_star and isinstance(wealth_star, str):
        wealth_star = wealth_star.strip() or None
    
    # 飞化：默认 False
    birth_data = {
        "marriage_palace_star": marriage_star,
        "wealth_palace_star": wealth_star,
        "transformations": {
            "hualu": bool(_safe_get(ocr_result, "transformations", "hualu", default=False)),
            "huaji": bool(_safe_get(ocr_result, "transformations", "huaji", default=False)),
        }
    }
    
    return {
        "name": name,
        "gender": gender,
        "birth_time": birth_time,
        "birth_data": birth_data
    }
