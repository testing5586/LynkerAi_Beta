"""
命盘导入 API Blueprint
Import API - 前端页面 + JSON/OCR 接口
"""

import os
import json
from flask import Blueprint, request, jsonify, render_template
from supabase import create_client
from .normalize_chart import normalize_from_wenmote
from .ocr_importer import process_image_bytes, save_record

bp_import = Blueprint("bp_import", __name__, url_prefix="/admin/import")

@bp_import.route("/", methods=["GET"])
def page():
    """导入中心首页"""
    return render_template("import_ui.html")

@bp_import.route("/json", methods=["POST"])
def upload_json():
    """
    接收单个文墨 JSON 文件
    POST /admin/import/json
    """
    f = request.files.get("file")
    if not f:
        return jsonify({"ok": False, "error": "未上传文件"}), 400
    
    try:
        content = f.read().decode("utf-8")
        data = json.loads(content)
        norm = normalize_from_wenmote(data)
        
        # 直接写库
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        sb = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        resp = sb.table("birthcharts").insert({
            "name": norm["name"],
            "gender": norm["gender"],
            "birth_time": norm["birth_time"],
            "ziwei_palace": None,
            "main_star": None,
            "shen_palace": None,
            "birth_data": norm["birth_data"]
        }).execute()
        
        print(f"✅ JSON 导入成功: {norm['name']}")
        return jsonify({"ok": True, "inserted": resp.data})
        
    except json.JSONDecodeError as e:
        return jsonify({"ok": False, "error": f"JSON 格式错误: {str(e)}"}), 400
    except Exception as e:
        print(f"❌ JSON 导入失败: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@bp_import.route("/ocr/preview", methods=["POST"])
def ocr_preview():
    """
    传图 → OCR → 抽取字段（不写库）→ 前端可让用户修正再提交
    POST /admin/import/ocr/preview
    """
    f = request.files.get("image")
    if not f:
        return jsonify({"ok": False, "error": "未上传图片"}), 400
    
    try:
        parsed = process_image_bytes(f.read())
        
        if "error" in parsed and parsed["error"]:
            return jsonify({"ok": False, "error": parsed["error"]}), 500
        
        print(f"✅ OCR 预览成功: {parsed.get('name', '未识别')}")
        return jsonify({"ok": True, "parsed": parsed})
        
    except Exception as e:
        print(f"❌ OCR 预览失败: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@bp_import.route("/ocr/confirm", methods=["POST"])
def ocr_confirm():
    """
    前端把修正后的字段 JSON 传回 → 写库
    POST /admin/import/ocr/confirm
    """
    try:
        payload = request.get_json(force=True)
        resp = save_record(payload)
        
        print(f"✅ OCR 确认导入: {payload.get('name', '未知')}")
        return jsonify({"ok": True, "inserted": resp.data})
        
    except Exception as e:
        print(f"❌ OCR 确认失败: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500
