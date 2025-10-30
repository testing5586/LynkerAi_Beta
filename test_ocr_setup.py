"""
测试 OCR 设置是否正常工作
Test OCR Setup
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_pytesseract_ocr():
    """测试 pytesseract OCR 功能"""
    try:
        from admin_dashboard.import_engine.ocr_importer_pytesseract import OCR_AVAILABLE, process_image_bytes

        if not OCR_AVAILABLE:
            print("❌ pytesseract OCR 不可用")
            return False

        print("✅ pytesseract OCR 已安装并可用")

        # 创建一个简单的测试图片
        from PIL import Image, ImageDraw, ImageFont
        import io

        # 创建一个包含文本的测试图片
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)

        # 添加测试文本
        text = "姓名: 张三\n性别: 男\n出生: 1990-01-01"
        draw.text((20, 20), text, fill='black')

        # 转换为字节
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()

        # 测试 OCR
        result = process_image_bytes(img_bytes)

        if result.get("error"):
            print(f"⚠️ OCR 识别遇到问题: {result['error']}")
            return False

        print(f"✅ OCR 识别成功")
        print(f"识别的文本: {result.get('raw_text', '')[:100]}...")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_easyocr():
    """测试 EasyOCR 功能（可选）"""
    try:
        from admin_dashboard.import_engine.ocr_importer import OCR_AVAILABLE

        if OCR_AVAILABLE:
            print("✅ EasyOCR 也可用（更高准确度）")
            return True
        else:
            print("ℹ️ EasyOCR 未安装（可选，需要 PyTorch）")
            return False

    except Exception as e:
        print("ℹ️ EasyOCR 未安装（可选，需要 PyTorch）")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("OCR 配置测试")
    print("=" * 50)

    # 测试 pytesseract
    print("\n[1/2] 测试 pytesseract OCR...")
    pytesseract_ok = test_pytesseract_ocr()

    # 测试 EasyOCR
    print("\n[2/2] 测试 EasyOCR...")
    easyocr_ok = test_easyocr()

    print("\n" + "=" * 50)
    print("测试结果总结:")
    print("=" * 50)

    if pytesseract_ok:
        print("✅ OCR 功能已就绪！可以使用图片上传功能。")
        print("   使用的引擎: pytesseract (轻量级)")
    elif easyocr_ok:
        print("✅ OCR 功能已就绪！可以使用图片上传功能。")
        print("   使用的引擎: EasyOCR (高准确度)")
    else:
        print("❌ OCR 功能未正确配置")
        print("   请确保已安装 Tesseract-OCR: https://github.com/tesseract-ocr/tesseract")

    print("=" * 50)
