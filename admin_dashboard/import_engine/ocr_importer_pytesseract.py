"""
OCR 导入器（pytesseract）- 轻量级OCR实现
Lightweight OCR Importer using pytesseract
"""

import os
import re
import io
from PIL import Image

# 动态加载 OCR 依赖（可选）
try:
    import pytesseract

    # 在 Windows 上设置 Tesseract 路径
    if os.name == 'nt':  # Windows
        # 尝试常见的 Tesseract 安装路径
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Tesseract-OCR\tesseract.exe"
        ]

        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                print(f"[OCR] Found Tesseract at: {path}")
                break

    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    pytesseract = None

def ocr_extract_fields(image_bytes):
    """
    从图片中提取命盘字段
    Returns: dict with extracted fields
    """
    if not OCR_AVAILABLE:
        return {
            "error": "OCR 功能未安装，请运行: pip install pytesseract",
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

        # 使用pytesseract进行OCR识别（中文+英文）
        # 需要安装Tesseract-OCR: https://github.com/tesseract-ocr/tesseract
        text = pytesseract.image_to_string(img, lang='chi_sim+eng')

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
        m = re.search(pattern, text, re.IGNORECASE)
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

def process_image_bytes(image_bytes):
    """
    处理图片字节流
    HTTP 路由会调用：传入 image bytes，返回抽取结果（前端可编辑后再提交）
    """
    parsed = ocr_extract_fields(image_bytes)
    return parsed
