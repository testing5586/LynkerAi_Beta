"""
真命盘验证中心 - Flask 路由
提供 Wizard 问答 + 命盘导入 + 评分确认的完整流程
"""
import os
import json
from flask import Blueprint, request, jsonify, render_template, session
from supabase import create_client

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from verification.verifier import verify_raw
from verify.utils import merge_manual_fields, normalize_gender
from verify.scorer import score_match
from verify.ai_prompts import get_primary_ai_prompt, get_ai_names_from_db
from verify.ai_verifier import verify_chart_with_ai, verify_chart_without_ai

bp = Blueprint("verify_wizard", __name__, url_prefix="/verify")

# 初始化 Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
sp = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None


@bp.get("")
def render_page():
    """
    渲染真命盘验证中心主页
    需要用户登录（从 session 获取 user_id）
    """
    user_id = session.get("user_id") or request.args.get("user_id")
    
    if not user_id:
        return jsonify({
            "ok": False,
            "toast": "请先登录后再使用真命盘验证功能"
        }), 401
    
    return render_template("verify_wizard.html", user_id=user_id)


@bp.post("/api/preview")
def preview():
    """
    预览评分接口
    接收：wizard + notes + 命盘文本/文件 + 手动字段 + (可选)use_ai + chart_type + life_events
    返回：parsed + score + candidates + (可选)ai_verification
    """
    import asyncio
    
    data = request.json or {}
    
    wizard = data.get("wizard", {})
    notes = data.get("notes", "")
    raw_text = data.get("raw_text", "")
    manual = data.get("manual", {})
    
    # 新增：AI验证选项
    use_ai = data.get("use_ai", False)
    chart_type = data.get("chart_type", "bazi")  # 'bazi' 或 'ziwei'
    life_events = data.get("life_events", "")  # 用户讲述的人生事件
    user_id = data.get("user_id")
    
    if not raw_text.strip():
        return jsonify({
            "ok": False,
            "toast": "请先输入或上传命盘文本"
        }), 400
    
    try:
        # 1. 调用现有解析器
        result = verify_raw(raw_text)
        parsed = result["parsed"]
        
        # 2. 标准化性别
        if manual.get("gender"):
            manual["gender"] = normalize_gender(manual["gender"])
        
        # 3. 合并手动字段
        parsed = merge_manual_fields(parsed, manual)
        
        # 4. 执行匹配评分
        score_result = score_match(parsed, wizard, notes)
        
        response_data = {
            "ok": True,
            "parsed": parsed,
            "score": score_result["score"],
            "weights": score_result["weights"],
            "signals": score_result["signals"],
            "candidates": score_result["candidates"],
            "toast": f"识别成功！匹配评分：{score_result['score']:.2f}"
        }
        
        # 5. (可选) 使用Child AI验证
        if use_ai and life_events:
            try:
                # 获取用户的AI名字
                _, bazi_name, ziwei_name = get_ai_names_from_db(user_id, sp) if sp and user_id else ("", "八字观察员", "星盘参谋")
                ai_name = bazi_name if chart_type == "bazi" else ziwei_name
                
                # 调用Child AI验证 (同步版本)
                ai_result = asyncio.run(verify_chart_with_ai(parsed, life_events, chart_type, ai_name))
                response_data["ai_verification"] = ai_result
                response_data["toast"] = f"AI验证完成！匹配度：{ai_result['score']:.2f}"
            except Exception as ai_error:
                print(f"⚠️ AI验证失败，使用降级方案: {ai_error}")
                # 降级到规则验证
                ai_result = verify_chart_without_ai(parsed)
                response_data["ai_verification"] = ai_result
                response_data["ai_verification"]["fallback"] = True
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "toast": f"识别失败：{str(e)}"
        }), 500


@bp.post("/api/submit")
def submit():
    """
    提交验证接口
    保存到 verified_charts 表
    """
    if not sp:
        return jsonify({
            "ok": False,
            "toast": "数据库未配置，无法保存"
        }), 500
    
    data = request.json or {}
    
    user_id = data.get("user_id")
    wizard = data.get("wizard", {})
    notes = data.get("notes", "")
    raw_text = data.get("raw_text", "")
    manual = data.get("manual", {})
    
    if not user_id:
        return jsonify({
            "ok": False,
            "toast": "缺少用户ID，请重新登录"
        }), 400
    
    if not raw_text.strip():
        return jsonify({
            "ok": False,
            "toast": "请先输入或上传命盘文本"
        }), 400
    
    try:
        # 1. 解析命盘
        result = verify_raw(raw_text)
        parsed = result["parsed"]
        
        # 2. 标准化性别
        if manual.get("gender"):
            manual["gender"] = normalize_gender(manual["gender"])
        
        # 3. 合并手动字段
        parsed = merge_manual_fields(parsed, manual)
        
        # 4. 评分
        score_result = score_match(parsed, wizard, notes)
        
        # 5. 验证必填字段
        if not parsed.get("name") or not parsed.get("gender"):
            return jsonify({
                "ok": False,
                "toast": "姓名和性别不能为空，请填写后重新提交"
            }), 400
        
        # 6. 写入 verified_charts 表
        record = sp.table("verified_charts").insert({
            "user_id": int(user_id),
            "source_text": raw_text,
            "parsed": json.dumps(parsed, ensure_ascii=False),
            "wizard": json.dumps(wizard, ensure_ascii=False),
            "notes": notes,
            "candidates": json.dumps(score_result["candidates"], ensure_ascii=False),
            "chosen_id": None,
            "score": float(score_result["score"])
        }).execute()
        
        record_id = record.data[0]["id"] if record.data else None
        
        return jsonify({
            "ok": True,
            "record_id": record_id,
            "score": score_result["score"],
            "candidates": score_result["candidates"],
            "toast": "我已为你保管这份记录。你可以随时回来查看和确认。"
        })
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "toast": f"保存失败：{str(e)}"
        }), 500


@bp.post("/api/confirm")
def confirm():
    """
    确认候选命盘接口
    用户选择某个候选后，更新 verified_charts.chosen_id
    """
    if not sp:
        return jsonify({
            "ok": False,
            "toast": "数据库未配置"
        }), 500
    
    data = request.json or {}
    
    record_id = data.get("record_id")
    chosen_id = data.get("chosen_id")
    
    if not record_id:
        return jsonify({
            "ok": False,
            "toast": "缺少记录ID"
        }), 400
    
    try:
        # 更新 chosen_id
        sp.table("verified_charts").update({
            "chosen_id": chosen_id
        }).eq("id", record_id).execute()
        
        return jsonify({
            "ok": True,
            "toast": "确认成功！这份命盘已归档到你的档案中。"
        })
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "toast": f"确认失败：{str(e)}"
        }), 500


@bp.post("/api/ocr")
def ocr_placeholder():
    """
    OCR 接口占位
    暂不启用，引导用户使用粘贴文本/上传TXT
    """
    return jsonify({
        "ok": False,
        "toast": "暂不启用 OCR 识别，请优先粘贴文本或上传 TXT 文件"
    }), 400


@bp.post("/api/chat")
def chat():
    """
    Primary AI 聊天接口
    处理用户与温柔陪伴者AI的对话
    """
    from openai import OpenAI
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or os.getenv("LYNKER_MASTER_KEY"))
    
    if not client.api_key:
        return jsonify({
            "ok": False,
            "message": "系统配置错误，请联系管理员"
        }), 500
    
    data = request.json or {}
    user_id = data.get("user_id")
    user_message = data.get("message", "").strip()
    conversation_history = data.get("history", [])  # 对话历史
    
    if not user_id:
        return jsonify({
            "ok": False,
            "message": "缺少用户ID"
        }), 400
    
    if not user_message:
        return jsonify({
            "ok": False,
            "message": "消息不能为空"
        }), 400
    
    try:
        # 获取用户自定义的AI名字
        primary_ai_name, _, _ = get_ai_names_from_db(user_id, sp) if sp else ("灵伴", "", "")
        
        # 获取Primary AI的系统Prompt
        system_prompt = get_primary_ai_prompt(primary_ai_name)
        
        # 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加历史对话（最多保留最近10轮）
        if conversation_history:
            messages.extend(conversation_history[-20:])  # 保留最近20条消息（10轮对话）
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        # 调用OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        ai_reply = response.choices[0].message.content.strip()
        
        return jsonify({
            "ok": True,
            "message": ai_reply,
            "ai_name": primary_ai_name
        })
    
    except Exception as e:
        print(f"❌ Primary AI 对话失败: {e}")
        return jsonify({
            "ok": False,
            "message": f"抱歉，我现在有些不舒服，请稍后再试。（{str(e)}）"
        }), 500
