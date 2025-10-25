"""
OCR 导入器（EasyOCR）- 带半自动解析 + 人工确认
OCR Importer with Semi-Auto Parsing
"""

import os
import re
import io
from supabase import create_client
from .normalize_chart import normalize_from_ocr

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
sb = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# 动态加载 OCR 依赖（可选）
try:
    from PIL import Image
    import numpy as np
    import easyocr
    reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    reader = None

def ocr_extract_fields(image_bytes):
    """
    从图片中提取命盘字段
    Returns: dict with extracted fields
    """
    if not OCR_AVAILABLE:
        return {
            "error": "OCR 功能未安装，请运行: pip install pillow easyocr",
            "name": None,
            "gender": None,
            "birth_time": None,
            "marriage_palace_star": None,
            "wealth_palace_star": None,
            "transformations": {"hualu": False, "huaji": False},
            "raw_text": "OCR 功能未启用"
        }
    
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_array = np.array(img)
        res = reader.readtext(img_array, detail=0)
        text = "\n".join(res)
    except Exception as e:
        return {
            "error": f"OCR 识别失败: {str(e)}",
            "name": None,
            "gender": None,
            "birth_time": None,
            "marriage_palace_star": None,
            "wealth_palace_star": None,
            "transformations": {"hualu": False, "huaji": False},
            "raw_text": ""
        }

    def find(pattern, default=None):
        m = re.search(pattern, text)
        return m.group(1).strip() if m else default

    # 简单规则：按常用截图模板扩展关键词
    name = find(r"(?:姓名|name)[:：]\s*([^\n]+)")
    gender = find(r"(?:性别|gender)[:：]\s*([男女])")
    birth_time = find(r"(?:出生|生辰|birth)[:：]\s*([0-9T:\- ]+)")
    marriage_star = find(r"(?:夫妻宫)[:：]?\s*([^\s/，,]+)")
    wealth_star = find(r"(?:财帛宫)[:：]?\s*([^\s/，,]+)")

    # 飞化：识别到关键词就先标 True
    hualu = bool(re.search(r"(化禄|HuaLu)", text))
    huaji = bool(re.search(r"(化忌|HuaJi)", text))

    return {
        "name": name,
        "gender": gender,
        "birth_time": birth_time,
        "marriage_palace_star": marriage_star,
        "wealth_palace_star": wealth_star,
        "transformations": {"hualu": hualu, "huaji": huaji},
        "raw_text": text
    }

def save_record(ocr_obj):
    """保存 OCR 识别后的记录到数据库"""
    if not sb:
        raise Exception("Supabase 客户端未初始化")
    
    norm = normalize_from_ocr(ocr_obj)
    
    return sb.table("birthcharts").insert({
        "name": norm["name"],
        "gender": norm["gender"],
        "birth_time": norm["birth_time"],
        "ziwei_palace": None,
        "main_star": None,
        "shen_palace": None,
        "birth_data": norm["birth_data"]
    }).execute()

def process_image_bytes(image_bytes):
    """
    处理图片字节流
    HTTP 路由会调用：传入 image bytes，返回抽取结果（前端可编辑后再提交）
    """
    parsed = ocr_extract_fields(image_bytes)
    return parsed
