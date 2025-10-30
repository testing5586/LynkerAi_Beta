# admin_dashboard/verify/ocr_wenmo_auto.py
# -*- coding: utf-8 -*-
"""
文墨天机命盘 OCR 自动识别器
- 支持 图片 → Gemini Vision → 文本 → 结构化
- 支持 纯文本（用户粘贴文墨命盘）→ 结构化
- 自动判断：八字 / 紫微
"""

import os
import re
import json
from typing import Dict, Any, List

# 如果你已经在别处配置过，就删掉这里这两行
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
except ImportError:
    GEMINI_AVAILABLE = False
    GEMINI_API_KEY = ""


# --------- 工具函数 ---------
WENMO_ZIWEI_KEYWORDS = [
    "文墨天機紫微斗數命盤", "文墨天机紫微斗数命盘", "命盤十二宮", "命盘十二宫", "命宮", "父母宮", "兄弟宮",
    "福德宮", "田宅宮", "官祿宮", "遷移宮", "夫妻宮", "子女宮", "財帛宮"
]
WENMO_BAZI_KEYWORDS = [
    "節氣四柱", "节气四柱", "非節氣四柱", "非节气四柱", "農曆時間", "农历时间", "真太陽時", "真太阳时"
]


def looks_like_ziwei(text: str) -> bool:
    text = text.replace(" ", "")
    for kw in WENMO_ZIWEI_KEYWORDS:
        if kw in text:
            return True
    return False


def looks_like_bazi(text: str) -> bool:
    text = text.replace(" ", "")
    for kw in WENMO_BAZI_KEYWORDS:
        if kw in text:
            return True
    # 文墨八字经常有这句
    if re.search(r"[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]\s+[甲乙丙丁戊己庚辛壬癸]", text):
        return True
    return False


# --------- 文墨八字解析 ---------
def parse_wenmo_bazi_text(text: str) -> Dict[str, Any]:
    """
    从文墨天机导出的文字中解析八字四柱 + 藏干 + 神煞 + 十神（副星）
    """
    result = {
        "type": "bazi",
        "source": "文墨天机",
        "raw": text,
        "birth_info": {},
        "四柱": {}
    }

    # 出生时间块
    birth_info = {}
    m = re.search(r"鐘錶時間[:：]\s*([0-9\-:\s]+)", text)
    if not m:
        m = re.search(r"钟表时间[:：]\s*([0-9\-:\s]+)", text)
    if m:
        birth_info["钟表时间"] = m.group(1).strip()

    m = re.search(r"真太陽時[:：]\s*([0-9\-:\s]+)", text)
    if not m:
        m = re.search(r"真太阳时[:：]\s*([0-9\-:\s]+)", text)
    if m:
        birth_info["真太阳时"] = m.group(1).strip()

    m = re.search(r"農曆時間[:：]\s*(.+)", text)
    if not m:
        m = re.search(r"农历时间[:：]\s*(.+)", text)
    if m:
        birth_info["农历时间"] = m.group(1).strip()

    m = re.search(r"[节節]气四柱[:：]\s*(.+)", text)
    if m:
        birth_info["节气四柱"] = m.group(1).strip()

    result["birth_info"] = birth_info

    # 节气四柱 → 年月日时
    year_pillar = month_pillar = day_pillar = hour_pillar = ""
    if "节气四柱" in birth_info:
        cols = re.findall(r"[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]", birth_info["节气四柱"])
        if len(cols) >= 4:
            year_pillar, month_pillar, day_pillar, hour_pillar = cols[:4]

    # 文墨导出那种"天干：… 地支：…"表格有时不会出现，
    # 所以我们给四柱先建结构，等待后面"藏干 / 副星 / 神煞"去补
    result["四柱"] = {
        "年柱": {
            "pillar": year_pillar,
            "天干": year_pillar[:1] if year_pillar else "",
            "地支": year_pillar[1:] if year_pillar else "",
            "藏干": [],
            "副星": [],
            "神煞": []
        },
        "月柱": {
            "pillar": month_pillar,
            "天干": month_pillar[:1] if month_pillar else "",
            "地支": month_pillar[1:] if month_pillar else "",
            "藏干": [],
            "副星": [],
            "神煞": []
        },
        "日柱": {
            "pillar": day_pillar,
            "天干": day_pillar[:1] if day_pillar else "",
            "地支": day_pillar[1:] if day_pillar else "",
            "藏干": [],
            "副星": [],
            "神煞": []
        },
        "时柱": {
            "pillar": hour_pillar,
            "天干": hour_pillar[:1] if hour_pillar else "",
            "地支": hour_pillar[1:] if hour_pillar else "",
            "藏干": [],
            "副星": [],
            "神煞": []
        }
    }

    # 识别类似你贴的这一段：
    # 藏干,戊土<br>乙木<br>癸水,乙木,己土<br>癸水<br>辛金,戊土<br>乙木<br>癸水
    # 副星,伤官<br>偏印<br>七杀,偏印,食神<br>七杀<br>偏财,伤官<br>偏印<br>七杀
    # 神煞,国印贵人<br>太极贵人<br>月德合,太极贵人<br>月德合,阴差阳错...
    def extract_row(label: str) -> List[List[str]]:
        # 找到以 label 开头的一行
        pattern = rf"{label}[，,](.+)"
        m = re.search(pattern, text)
        if not m:
            return []
        row = m.group(1).strip()
        # 按列拆
        cols = re.split(r"[，,]", row)
        all_cols = []
        for col in cols:
            # 再按 <br> 拆
            items = re.split(r"<br>|<br/>|<br />|\s+", col.strip())
            # 过滤空
            items = [x for x in items if x]
            all_cols.append(items)
        return all_cols

    zanggan_cols = extract_row("藏干")
    fuxing_cols = extract_row("副星")
    shensha_cols = extract_row("神煞")

    # 按顺序填 年 月 日 时
    columns = ["年柱", "月柱", "日柱", "时柱"]
    for idx, col_name in enumerate(columns):
        if idx < len(zanggan_cols):
            result["四柱"][col_name]["藏干"] = zanggan_cols[idx]
        if idx < len(fuxing_cols):
            result["四柱"][col_name]["副星"] = fuxing_cols[idx]
        if idx < len(shensha_cols):
            result["四柱"][col_name]["神煞"] = shensha_cols[idx]

    result["confidence"] = 0.9  # 文本方式一般比较高
    return result


# --------- 文墨紫微解析 ---------
def parse_wenmo_ziwei_text(text: str) -> Dict[str, Any]:
    """
    文墨紫微的结构其实很规整：
    ├父母宮[戊子]
    │ ├主星 : 武曲[旺][生年權][↑忌],天府[廟]
    │ ├輔星 : 无
    │ ├小星 : ...
    我们把每个"├xxx宮[...]"当成一宫来拆
    """
    result = {
        "type": "ziwei",
        "source": "文墨天机",
        "raw": text,
        "基本信息": {},
        "命盘十二宫": {}
    }

    # 基本信息
    base_keys = {
        "性别": r"性别\s*[:：]\s*(.+)",
        "钟表时间": r"钟表时间\s*[:：]\s*([0-9\-\s:]+)",
        "真太阳时": r"真太陽時\s*[:：]\s*([0-9\-\s:]+)|真太阳时\s*[:：]\s*([0-9\-\s:]+)",
        "农历时间": r"農曆時間\s*[:：]\s*(.+)|农历时间\s*[:：]\s*(.+)",
        "节气四柱": r"[节節]气四柱\s*[:：]\s*(.+)",
        "非节气四柱": r"非[节節]气四柱\s*[:：]\s*(.+)",
        "命主": r"命主\s*[:：]\s*(.+)",
        "身主": r"身主\s*[:：]\s*(.+)"
    }
    base_info = {}
    for key, pat in base_keys.items():
        m = re.search(pat, text)
        if m:
            # 兼容两个分组
            val = m.group(1) if m.group(1) else (m.group(2) if m.lastindex and m.lastindex >= 2 else "")
            base_info[key] = val.strip()
    result["基本信息"] = base_info

    # 十二宫
    # 用一个粗暴但好用的正则：匹配以"├父母宮[戊子]"开头到下一个"├"之前的全部
    palace_pattern = r"├([^\n\r\[]+宮)\[([^\]]+)\]([\s\S]*?)(?=├[^\n\r\[]+宮|\Z)"
    palaces = re.findall(palace_pattern, text)
    for palace_name, palace_branch, palace_body in palaces:
        palace_name = palace_name.strip()
        palace_data = {
            "宫支": palace_branch.strip(),
            "主星": [],
            "辅星": [],
            "小星": [],
            "神煞": [],
            "大限": None,
            "小限": None,
            "流年": None
        }

        # 主星
        m_main = re.search(r"主星\s*[:：]\s*(.+)", palace_body)
        if m_main:
            # 文墨主星有 ", " 分隔
            main_stars = [x.strip() for x in re.split(r"[，,]", m_main.group(1)) if x.strip()]
            palace_data["主星"] = main_stars

        m_fu = re.search(r"輔星\s*[:：]\s*(.+)", palace_body)
        if m_fu:
            fu_stars = [x.strip() for x in re.split(r"[，,]", m_fu.group(1)) if x.strip()]
            palace_data["辅星"] = fu_stars

        m_small = re.search(r"小星\s*[:：]\s*(.+)", palace_body)
        if m_small:
            small_stars = [x.strip() for x in re.split(r"[，,]", m_small.group(1)) if x.strip()]
            palace_data["小星"] = small_stars

        # 神煞这一块文墨是嵌套的，这里先全抓
        m_sha = re.search(r"神煞([\s\S]+?)\n", palace_body)
        if m_sha:
            # 取出多行中的第一行
            sha_line = m_sha.group(1)
            sha_items = [x.strip(" ：:") for x in re.split(r"[，,、]", sha_line) if x.strip(" ：:")]
            palace_data["神煞"] = sha_items

        # 大限 / 小限 / 流年
        m_daxian = re.search(r"大限\s*[:：]\s*([0-9~\s虛岁岁\-]+)", palace_body)
        if m_daxian:
            palace_data["大限"] = m_daxian.group(1).strip()
        m_xiaoxian = re.search(r"小限\s*[:：]\s*([0-9,、\s虛岁岁]+)", palace_body)
        if m_xiaoxian:
            palace_data["小限"] = m_xiaoxian.group(1).strip()
        m_liunian = re.search(r"流年\s*[:：]\s*([0-9,、\s虛岁岁]+)", palace_body)
        if m_liunian:
            palace_data["流年"] = m_liunian.group(1).strip()

        result["命盘十二宫"][palace_name] = palace_data

    result["confidence"] = 0.9
    return result


# --------- 图片 → Gemini → 文墨解析 ---------
def ocr_wenmo_auto_from_image(img_path: str) -> Dict[str, Any]:
    """
    用 Gemini Vision 先把图片转成文墨文本，再走上面的解析
    """
    if not GEMINI_AVAILABLE:
        return {"error": "Gemini API is not available. Please install google-generativeai"}
    
    if not GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY is not set"}

    try:
        # 使用旧版稳定模型 gemini-pro-vision
        model = genai.GenerativeModel("gemini-pro-vision")
        
        with open(img_path, "rb") as f:
            img_bytes = f.read()

        prompt = (
            "这是一张文墨天机生成的命理命盘截图，可能是八字命盘也可能是紫微斗数命盘。\n"
            "请先判断是哪一类：\n"
            "- 如果是紫微斗数，请完整按文墨天机的文字结构把12宫内容转成纯文本（保留树形格式）。\n"
            "- 如果是八字命盘，请完整转成含藏干, 副星, 神煞列的纯文本，就像你从文墨里复制出来的一样。\n"
            "不要加解释，不要多写，保持原有的字段名。"
        )

        res = model.generate_content([prompt, {"mime_type": "image/png", "data": img_bytes}])
        txt = res.text.strip()

        # 自动判断类型
        if looks_like_ziwei(txt):
            parsed = parse_wenmo_ziwei_text(txt)
        elif looks_like_bazi(txt):
            parsed = parse_wenmo_bazi_text(txt)
        else:
            # 无法判断就都给
            parsed = {
                "type": "unknown",
                "raw": txt
            }
        parsed["from"] = "gemini_vision"
        return parsed
        
    except Exception as e:
        # 返回详细错误信息
        error_msg = str(e)
        if "404" in error_msg and "model" in error_msg.lower():
            return {"error": "Gemini API 模型不可用。请检查您的 API 密钥是否有效，或者该 API 密钥是否有权限访问 Gemini 视觉模型。"}
        elif "401" in error_msg or "unauthorized" in error_msg.lower():
            return {"error": "Gemini API 密钥无效或未授权。请检查 GEMINI_API_KEY 环境变量。"}
        else:
            return {"error": f"Gemini Vision 识别失败: {error_msg}"}


# --------- 统一入口（文本 or 图片）---------
def ocr_wenmo_auto_from_text(text: str) -> Dict[str, Any]:
    if looks_like_ziwei(text):
        return parse_wenmo_ziwei_text(text)
    if looks_like_bazi(text):
        return parse_wenmo_bazi_text(text)
    return {"type": "unknown", "raw": text}
