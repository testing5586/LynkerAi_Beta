"""
真命盘验证系统 - Flask API
提供两个端点：
1. POST /verify/preview - 预览评分（不写数据库）
2. POST /verify/submit - 提交验证（写入数据库，分数>=0.8通过，否则拒绝）
"""
import os
import json
from flask import Blueprint, request, jsonify
from supabase import create_client
from .verifier import verify_raw

bp = Blueprint("verify", __name__, url_prefix="/verify")

# 初始化 Supabase 客户端
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
sp = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None


@bp.post("/preview")
def preview():
    """
    预览评分接口
    接收原始文本，返回解析结果和AI评分，不写入数据库
    """
    raw = request.json.get("raw_text", "")
    
    if not raw.strip():
        return jsonify({"ok": False, "error": "raw_text 不能为空"}), 400
    
    # 调用验证器
    result = verify_raw(raw)
    
    return jsonify({
        "ok": True,
        "parsed": result["parsed"],
        "score": result["score"]
    })


@bp.post("/submit")
def submit():
    """
    提交验证接口
    接收原始文本，进行评分，并根据分数决定入库策略：
    - score >= 0.8: 写入 birthcharts 表
    - score < 0.8: 记录日志，不写入数据库
    同时记录验证日志到文件
    """
    if not sp:
        return jsonify({"ok": False, "error": "Supabase 未配置"}), 500
    
    raw = request.json.get("raw_text", "")
    uploader_id = request.json.get("uploader_id", None)
    
    if not raw.strip():
        return jsonify({"ok": False, "error": "raw_text 不能为空"}), 400
    
    # 调用验证器
    ver = verify_raw(raw)
    parsed = ver["parsed"]
    score_data = ver["score"]
    final_score = score_data["score"]
    
    # 验证必填字段：姓名和性别
    if not parsed.get("name") or not parsed.get("gender"):
        return jsonify({
            "ok": False,
            "status": "rejected",
            "error": "姓名或性别缺失，请填写后重新提交",
            "parsed": parsed
        }), 400
    
    # 记录验证日志
    import datetime
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "score": final_score,
        "score_details": score_data,
        "parsed": parsed,
        "uploader_id": uploader_id
    }
    
    try:
        # 根据评分决定入库策略
        if final_score >= 0.8:
            # 通过验证，写入 birthcharts 表
            verified = sp.table("birthcharts").insert({
                "name": parsed.get("name", ""),
                "gender": parsed.get("gender", ""),
                "birth_time": parsed.get("birth_time") or None,
                "ziwei_palace": parsed.get("ziwei_palace", ""),
                "main_star": parsed.get("main_star", ""),
                "shen_palace": parsed.get("shen_palace", ""),
                "birth_data": json.dumps(parsed, ensure_ascii=False)
            }).execute().data[0]
            
            chart_id = verified["id"]
            status = "verified"
            message = f"✅ 验证通过！评分：{final_score}，已写入命盘库（ID: {chart_id}）"
            log_entry["status"] = "verified"
            log_entry["chart_id"] = chart_id
            
        else:
            # 未通过验证，仅记录日志
            status = "rejected"
            message = f"❌ 验证未通过。评分：{final_score}，建议补充更多信息后重新提交"
            log_entry["status"] = "rejected"
            log_entry["reason"] = f"评分 {final_score} < 0.8"
        
        # 写入日志文件
        try:
            import os
            log_dir = "logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            log_file = os.path.join(log_dir, "verification_log.jsonl")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as log_error:
            print(f"⚠️  日志写入失败: {log_error}")
        
        return jsonify({
            "ok": True,
            "status": status,
            "score": final_score,
            "score_details": score_data,
            "message": message
        })
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": f"数据库操作失败: {str(e)}"
        }), 500
