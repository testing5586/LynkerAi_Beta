"""
PaddleOCR 实现 - 高精度中文 OCR
适用于八字命盘和紫微斗数命盘的图片识别
"""
import io

try:
    from PIL import Image
    from paddleocr import PaddleOCR
    import numpy as np
    
    # 初始化 PaddleOCR (只需运行一次)
    # use_angle_cls=True 表示使用文本方向分类器
    # lang='ch' 表示中文识别
    ocr = PaddleOCR(use_angle_cls=True, lang='ch')
    OCR_AVAILABLE = True
    print("✅ PaddleOCR 已成功初始化 (中文识别)")
except ImportError as e:
    OCR_AVAILABLE = False
    ocr = None
    print(f"⚠️ PaddleOCR 未安装: {e}")
except Exception as e:
    OCR_AVAILABLE = False
    ocr = None
    print(f"⚠️ PaddleOCR 初始化失败: {e}")

def ocr_extract_fields(image_bytes):
    """
    使用 PaddleOCR 从图片中提取命盘字段
    Returns: dict with extracted fields
    """
    if not OCR_AVAILABLE:
        return {
            "error": "OCR 功能未安装，请运行: pip install paddleocr paddlepaddle",
            "name": None,
            "gender": None,
            "birth_time": None,
            "marriage_palace_star": None,
            "wealth_palace_star": None,
            "transformations": {"hualu": False, "huaji": False},
            "raw_text": "OCR 功能未启用"
        }
    
    try:
        # 打开图片
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_array = np.array(img)
        
        # 使用 PaddleOCR 进行识别
        result = ocr.ocr(img_array, cls=True)
        
        # 提取文本 (PaddleOCR 返回格式: [[[box], (text, confidence)], ...])
        text_lines = []
        if result and result[0]:
            for line in result[0]:
                if line and len(line) >= 2:
                    text_content = line[1][0]  # (text, confidence) -> text
                    text_lines.append(text_content)
        
        raw_text = "\n".join(text_lines)
        
        print(f"📝 PaddleOCR 识别结果 ({len(text_lines)} 行):")
        print(raw_text[:300])  # 打印前300个字符
        
    except Exception as e:
        print(f"❌ PaddleOCR 识别失败: {e}")
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
    
    # 基础字段抽取（可根据实际命盘格式调整）
    extracted = {
        "name": None,
        "gender": None,
        "birth_time": None,
        "marriage_palace_star": None,
        "wealth_palace_star": None,
        "transformations": {"hualu": False, "huaji": False},
        "raw_text": raw_text
    }
    
    # 简单的字段识别逻辑
    for line in text_lines:
        line_lower = line.lower()
        
        # 识别姓名
        if "姓名" in line or "name" in line_lower:
            # 提取冒号后的内容
            if ":" in line or "：" in line:
                name_part = line.split(":" if ":" in line else "：")[-1].strip()
                if name_part and len(name_part) < 20:
                    extracted["name"] = name_part
        
        # 识别性别
        if "性别" in line or "gender" in line_lower:
            if "男" in line:
                extracted["gender"] = "男"
            elif "女" in line:
                extracted["gender"] = "女"
        
        # 识别出生时间
        if "出生" in line or "生日" in line or "birth" in line_lower:
            # 尝试提取时间信息
            if ":" in line or "：" in line:
                time_part = line.split(":" if ":" in line else "：")[-1].strip()
                if time_part and len(time_part) < 50:
                    extracted["birth_time"] = time_part
        
        # 识别化禄/化忌
        if "化禄" in line:
            extracted["transformations"]["hualu"] = True
        if "化忌" in line:
            extracted["transformations"]["huaji"] = True
    
    return extracted


def process_image_bytes(image_bytes):
    """
    处理图片字节流 - PaddleOCR 版本
    HTTP 路由会调用：传入 image bytes，返回抽取结果（前端可编辑后再提交）
    """
    parsed = ocr_extract_fields(image_bytes)
    return parsed
