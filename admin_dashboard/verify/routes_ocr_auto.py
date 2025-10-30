# admin_dashboard/verify/routes_ocr_auto.py
# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
import os
from .ocr_wenmo_auto import (
    ocr_wenmo_auto_from_image,
    ocr_wenmo_auto_from_text
)

ocr_auto_bp = Blueprint("ocr_auto_bp", __name__)
UPLOAD_DIR = "/tmp/lynker_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@ocr_auto_bp.route("/api/ocr_wenmo_auto", methods=["POST"])
def api_ocr_wenmo_auto():
    """
    前端统一上传入口：
    - 如果有 file → 当成图片 → Gemini Vision
    - 如果有 text → 当成文墨文本 → 走文本解析
    返回一定是文墨风格的 JSON
    """
    try:
        if "file" in request.files:
            f = request.files["file"]
            save_path = os.path.join(UPLOAD_DIR, f.filename)
            f.save(save_path)
            data = ocr_wenmo_auto_from_image(save_path)
            
            # 检查是否返回错误
            if "error" in data:
                return jsonify({"ok": False, "error": data["error"]}), 400
            
            return jsonify({"ok": True, "data": data})

        data = request.get_json(silent=True) or {}
        text = data.get("text", "").strip()
        if text:
            parsed = ocr_wenmo_auto_from_text(text)
            
            # 检查是否返回错误
            if "error" in parsed:
                return jsonify({"ok": False, "error": parsed["error"]}), 400
            
            return jsonify({"ok": True, "data": parsed})

        return jsonify({"ok": False, "error": "no file or text"}), 400
    
    except Exception as e:
        # 捕获所有异常，返回友好的 JSON 错误
        return jsonify({"ok": False, "error": str(e)}), 500
