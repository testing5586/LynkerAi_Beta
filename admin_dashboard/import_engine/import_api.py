"""
命盘导入 API Blueprint
Import API - 前端页面 + JSON/OCR/TXT/DOC 多格式接口
"""

import os
import json
from flask import Blueprint, request, jsonify, render_template
from supabase import create_client
from .normalize_chart import normalize_from_wenmote
from .ocr_importer import process_image_bytes, save_record as ocr_save
from .txt_importer import process_txt_file, save_record as txt_save
from .doc_importer import process_docx_file, save_record as doc_save

bp_import = Blueprint("bp_import", __name__, url_prefix="/import")

@bp_import.route("/", methods=["GET"])
def page():
    """导入中心首页"""
    return render_template("import_ui.html")

@bp_import.route("/stats", methods=["GET"])
def get_stats():
    """获取命盘导入统计数据"""
    try:
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        sb = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # 查询总记录数
        result = sb.table("birthcharts").select("id", count="exact").execute()
        total = result.count if result.count else 0
        
        return jsonify({"ok": True, "total": total})
    except Exception as e:
        print(f"❌ 统计查询失败: {e}")
        return jsonify({"ok": False, "total": 0, "error": str(e)})

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
    POST /import/ocr/confirm
    """
    try:
        payload = request.get_json(force=True)
        resp = ocr_save(payload)
        
        print(f"✅ OCR 确认导入: {payload.get('name', '未知')}")
        return jsonify({"ok": True, "inserted": resp.data})
        
    except Exception as e:
        print(f"❌ OCR 确认失败: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@bp_import.route("/file/preview", methods=["POST"])
def file_preview():
    """
    通用文件上传预览接口 - 自动识别格式（.txt, .doc, .docx）
    POST /import/file/preview
    """
    f = request.files.get("file")
    if not f:
        return jsonify({"ok": False, "error": "未上传文件"}), 400
    
    filename = f.filename.lower()
    file_content = f.read()
    
    try:
        # 根据文件扩展名选择处理器
        if filename.endswith('.txt'):
            print(f"📝 处理 TXT 文件: {f.filename}")
            parsed = process_txt_file(file_content)
            file_type = "txt"
            
        elif filename.endswith('.docx'):
            print(f"📄 处理 DOCX 文件: {f.filename}")
            parsed, error = process_docx_file(file_content)
            if error:
                return jsonify({"ok": False, "error": error}), 500
            file_type = "docx"
            
        elif filename.endswith('.doc'):
            # .doc 格式需要转换（暂不支持，提示用户转为 .docx）
            return jsonify({
                "ok": False, 
                "error": "暂不支持 .doc 格式，请将文件另存为 .docx 格式后重新上传"
            }), 400
            
        else:
            return jsonify({
                "ok": False,
                "error": f"不支持的文件格式: {filename}，支持的格式: .txt, .docx"
            }), 400
        
        if "error" in parsed and parsed["error"]:
            return jsonify({"ok": False, "error": parsed["error"]}), 500
        
        print(f"✅ {file_type.upper()} 预览成功: {parsed.get('name', '未识别')}")
        return jsonify({"ok": True, "parsed": parsed, "file_type": file_type})
        
    except Exception as e:
        print(f"❌ 文件预览失败: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@bp_import.route("/file/confirm", methods=["POST"])
def file_confirm():
    """
    通用文件确认写入接口
    POST /import/file/confirm
    """
    try:
        payload = request.get_json(force=True)
        file_type = payload.get("file_type", "txt")
        
        # 根据文件类型选择保存函数
        if file_type == "txt":
            resp = txt_save(payload)
        elif file_type in ["doc", "docx"]:
            resp = doc_save(payload)
        else:
            resp = ocr_save(payload)  # 默认使用 OCR 保存
        
        print(f"✅ {file_type.upper()} 确认导入: {payload.get('name', '未知')}")
        return jsonify({"ok": True, "inserted": resp.data})
        
    except Exception as e:
        print(f"❌ 文件确认失败: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500
