"""
工具函数 - 手动字段合并逻辑
"""

def merge_manual_fields(parsed, manual):
    """
    合并手动输入字段到解析结果
    
    Args:
        parsed: AI 解析的命盘数据 dict
        manual: 手动输入数据 dict, 包含 {name, gender, name_locked}
    
    Returns:
        合并后的 parsed dict
    
    规则:
        - name_locked=True: 强制使用手动姓名/性别覆盖AI识别值
        - name_locked=False: AI值优先，手动值作为补充
    """
    parsed = dict(parsed or {})
    manual = manual or {}
    
    if manual.get("name_locked"):
        if manual.get("name"):
            parsed["name"] = manual["name"]
        if manual.get("gender"):
            parsed["gender"] = manual["gender"]
    else:
        parsed["name"] = parsed.get("name") or manual.get("name") or ""
        parsed["gender"] = parsed.get("gender") or manual.get("gender") or ""
    
    return parsed


def normalize_gender(gender):
    """
    标准化性别字段
    支持: male/female/男/女
    """
    if not gender:
        return ""
    g = str(gender).strip().lower()
    if g in ["male", "男"]:
        return "男"
    if g in ["female", "女"]:
        return "女"
    return gender
