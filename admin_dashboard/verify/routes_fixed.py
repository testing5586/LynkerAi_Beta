"""
真命盘验证中心 - Flask 路由
提供 Wizard 问答 + 命盘导入 + 评分确认的完整流程
"""
import os
import json
from flask import Blueprint, request, jsonify, render_template, session
from supabase import create_client

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from verification.verifier import verify_raw
from verify.utils import merge_manual_fields, normalize_gender
from verify.scorer import score_match
from verify.ai_prompts import get_primary_ai_prompt, get_ai_names_from_db
from verify.ai_verifier import verify_chart_with_ai, verify_chart_without_ai, get_current_uploaded_charts
from verify.child_ai_hints import generate_child_ai_hint
from verify.wizard_loader import load_latest_wizard

# Import validation manager with relative path to avoid circular imports
try:
    from ..lynker_engine.core.validation_manager import format_ai_response, parse_validation_click, create_validation_log
except ImportError:
    print("⚠️ 无法导入验证管理器，验证功能将不可用")
    # 提供降级函数
    def format_ai_response(text, chart_locked):
        return text
    
    def parse_validation_click(click_data):
        return {"valid": False, "error": "验证管理器不可用"}
    
    def create_validation_log(*args, **kwargs):
        return {}

bp = Blueprint("verify_wizard", __name__, url_prefix="/verify")

# 初始化 Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
sp = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None


def save_verification_results(user_id, group_index, bazi_result, ziwei_result, life_events_count, sp):
    """
    存储AI验证结果到 user_verification_results 表
    使用 upsert 策略：如果该用户的该组已有记录则更新，否则插入
    """
    try:
        # 检查是否已存在该用户该组的记录
        existing = sp.table("user_verification_results").select("id").eq("user_id", user_id).eq("group_index", group_index).execute()
        
        data = {
            "user_id": user_id,
            "group_index": group_index,
            "bazi_confidence": bazi_result.get("birth_time_confidence", "低"),
            "bazi_supporting_evidence": bazi_result.get("key_supporting_evidence", []),
            "bazi_conflicts": bazi_result.get("key_conflicts", []),
            "bazi_summary": bazi_result.get("summary", ""),
            "ziwei_confidence": ziwei_result.get("birth_time_confidence", "低"),
            "ziwei_supporting_evidence": ziwei_result.get("key_supporting_evidence", []),
            "ziwei_conflicts": ziwei_result.get("key_conflicts", []),
            "ziwei_summary": ziwei_result.get("summary", ""),
            "life_events_count": life_events_count,
            "updated_at": "now()"
        }
        
        if existing.data and len(existing.data) > 0:
            # 更新现有记录
            record_id = existing.data[0]["id"]
            sp.table("user_verification_results").update(data).eq("id", record_id).execute()
            print(f"✅ 更新验证结果: user_id={user_id}, group={group_index}")
        else:
            # 插入新记录
            sp.table("user_verification_results").insert(data).execute()
            print(f"✅ 插入验证结果: user_id={user_id}, group={group_index}")
        
    except Exception as e:
        print(f"❌ 存储验证结果失败: {e}")


def get_primary_context(user_id):
    """
    查询用户是否已上传命盘并返回相应的上下文
    """
    try:
        # 查询用户是否已上传命盘
        bazi = sp.table("verified_charts").select("*").eq("user_id", user_id).eq("chart_type", "bazi").execute().data
        ziwei = sp.table("verified_charts").select("*").eq("user_id", user_id).eq("chart_type", "ziwei").execute().data

        if not bazi or not ziwei:
            return "用户尚未上传命盘，请提示上传。"
        else:
            questionnaire = load_latest_wizard()
            return f"命盘数据已上传。\n请依据命盘与问卷结构开始验证：\n{questionnaire[:800]}"
    except Exception as e:
        print(f"⚠️ 获取命盘上下文失败: {e}")
        return "无法获取命盘数据，请继续对话。"


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
    group_index = data.get("group_index", 0)  # 当前组索引（0/1/2）
    
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
        
        # 5. 【重要】紫微命盘：移除错误的姓名/性别字段
        # 紫微命盘解析不应该包含 name/gender 字段
        # 这些字段常被误识别为命盘主星（巨门、天同、武曲等）
        if chart_type == "ziwei":
            parsed_for_display = {
                k: v for k, v in parsed.items() 
                if k not in ["name", "gender"]
            }
        else:
            parsed_for_display = parsed
        
        response_data = {
            "ok": True,
            "parsed": parsed_for_display,
            "score": score_result["score"],
            "weights": score_result["weights"],
            "signals": score_result["signals"],
            "candidates": score_result["candidates"],
            "toast": f"识别成功！匹配评分：{score_result['score']:.2f}"
        }
        
        # 5. [禁用] 自动触发AI验证
        # 新流程：验证移至问卷完成后在 /api/chat 中触发
        # 此处仅负责返回"命盘成功上传"状态
        
        # life_events_count = len([line for line in life_events.split('\n') if line.strip()]) if life_events else 0
        # auto_trigger_ai = life_events_count >= 3 and user_id
        
        # if auto_trigger_ai or (use_ai and life_events):
        #     try:
        #         # 获取用户的AI名字
        #         _, bazi_name, ziwei_name = get_ai_names_from_db(user_id, sp) if sp and user_id else ("", "八字观察员", "星盘参谋")
        #         
        #         # 同时验证八字和紫微（如果是自动触发）
        #         if auto_trigger_ai:
        #             # 调用两个Child AI验证
        #             bazi_result = asyncio.run(verify_chart_with_ai(parsed, life_events, "bazi", bazi_name))
        #             ziwei_result = asyncio.run(verify_chart_with_ai(parsed, life_events, "ziwei", ziwei_name))
        #             
        #             response_data["bazi_verification"] = bazi_result
        #             response_data["ziwei_verification"] = ziwei_result
        #             response_data["auto_verified"] = True
        #             response_data["toast"] = f"AI自动验证完成！八字匹配度：{bazi_result['score']:.2%}，紫微匹配度：{ziwei_result['score']:.2%}"
        #             
        #             # 存储验证结果到数据库
        #             if sp:
        #                 save_verification_results(
        #                     user_id=user_id,
        #                     group_index=group_index,
        #                     bazi_result=bazi_result,
        #                     ziwei_result=ziwei_result,
        #                     life_events_count=life_events_count,
        #                     sp=sp
        #                 )
        #         else:
        #             # 单个验证（手动触发）
        #             ai_name = bazi_name if chart_type == "bazi" else ziwei_name
        #             ai_result = asyncio.run(verify_chart_with_ai(parsed, life_events, chart_type, ai_name))
        #             response_data["ai_verification"] = ai_result
        #             response_data["toast"] = f"AI验证完成！匹配度：{ai_result['score']:.2f}"
        #             
        #     except Exception as ai_error:
        #         print(f"⚠️ AI验证失败，使用降级方案: {ai_error}")
        #         # 降级到规则验证
        #         ai_result = verify_chart_without_ai(parsed)
        #         response_data["ai_verification"] = ai_result
        #         response_data["ai_verification"]["fallback"] = True
        
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
    新增：检测问卷完成并触发AI验证
    新增：知识检索增强 (Retrieval Router)
    """
    import asyncio
    from openai import OpenAI
    
    # 导入知识检索路由
    KNOWLEDGE_AVAILABLE = False
    find_relevant_knowledge = None
    allow_access = None
    
    try:
        from knowledge.retrieval_router import find_relevant_knowledge
        from knowledge.access_control import allow_access
        KNOWLEDGE_AVAILABLE = True
    except ImportError:
        print("⚠️ 知识检索模块未找到，Primary AI 将不使用知识库增强")
    
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
    
    # 新增：命盘上传状态和当前组索引
    chart_uploaded = data.get("chart_uploaded", False)
    group_index = data.get("group_index", 0)
    life_events = data.get("life_events", "")  # 累积的人生事件
    parsed_chart = data.get("parsed_chart", {})  # 解析后的命盘数据
    
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
    
    # 【特殊触发】检测系统触发问卷开始
    if user_message == "__SYSTEM_TRIGGER_START_QUESTIONNAIRE__":
        # 加载问卷第一句话
        try:
            from verify.wizard_loader import load_latest_wizard
            questionnaire = load_latest_wizard()
            
            if questionnaire and questionnaire.get("questions"):
                first_question = questionnaire["questions"][0]
                question_text = first_question.get("question", "")
                options_text = ""
                
                if first_question.get("options"):
                    options_list = [f"({opt['id']}) {opt['text']}" for opt in first_question["options"]]
                    options_text = "\n" + "\n".join(options_list)
                
                questionnaire_start_message = f"我们先从家庭背景开始吧。\n{question_text}{options_text}"
                
                return jsonify({
                    "ok": True,
                    "message": questionnaire_start_message,
                    "ai_name": "灵伴",
                    "questionnaire_started": True
                })
            else:
                return jsonify({
                    "ok": True,
                    "message": "我们先从家庭背景开始吧。\n请告诉我，你的父母目前的状态是？\n(1) 双亲健在 (2) 父亡 (3) 母亡 (4) 离异 (5) 关系疏远",
                    "ai_name": "灵伴",
                    "questionnaire_started": True
                })
        except Exception as e:
            print(f"⚠️ 加载问卷失败: {e}")
            # 使用默认问卷第一句话
            return jsonify({
                "ok": True,
                "message": "我们先从家庭背景开始吧。\n请告诉我，你的父母目前的状态是？\n(1) 双亲健在 (2) 父亡 (3) 母亡 (4) 离异 (5) 关系疏远",
                "ai_name": "灵伴",
                "questionnaire_started": True
            })
    
    # 获取 AI 名称（从数据库 users 表）
    primary_ai_name = "灵伴"  # 默认名称
    bazi_name = "八字观察员"
    ziwei_name = "星盘参谋"
    
    if sp:
        try:
            user_data = sp.table("users").select("primary_ai_name").eq("id", user_id).execute()
            if user_data.data and len(user_data.data) > 0 and user_data.data[0].get("primary_ai_name"):
                primary_ai_name = user_data.data[0]["primary_ai_name"]
            
            # 获取 Child AI 名称
            ai_names = get_ai_names_from_db(sp)
            if ai_names:
                bazi_name = ai_names.get("bazi", "八字观察员")
                ziwei_name = ai_names.get("ziwei", "星盘参谋")
        except Exception as e:
            print(f"⚠️ 获取 AI 名称失败，使用默认值: {e}")
    
    try:
        # 【获取 Child AI 验证结果】从数据库读取最新的验证结果
        bazi_result = None
        ziwei_result = None
        
        if sp:
            try:
                # 从 user_verification_results 表获取最新验证结果
                verification_data = sp.table("user_verification_results") \
                    .select("bazi_confidence, bazi_supporting_evidence, bazi_conflicts, bazi_summary, ziwei_confidence, ziwei_supporting_evidence, ziwei_conflicts, ziwei_summary") \
                    .eq("user_id", user_id) \
                    .eq("group_index", group_index) \
                    .order("created_at", desc=True) \
                    .limit(1) \
                    .execute()
                
                if verification_data.data and len(verification_data.data) > 0:
                    v = verification_data.data[0]
                    
                    # 构建八字验证结果文本
                    if v.get("bazi_confidence"):
                        bazi_result = f"""置信度: {v['bazi_confidence']}
支持证据: {', '.join(v.get('bazi_supporting_evidence', []))}
冲突点: {', '.join(v.get('bazi_conflicts', []))}
总结: {v.get('bazi_summary', '')}"""
                    
                    # 构建紫微验证结果文本
                    if v.get("ziwei_confidence"):
                        ziwei_result = f"""置信度: {v['ziwei_confidence']}
支持证据: {', '.join(v.get('ziwei_supporting_evidence', []))}
冲突点: {', '.join(v.get('ziwei_conflicts', []))}
总结: {v.get('ziwei_summary', '')}"""
                        
                    print(f"✅ 已加载 Child AI 验证结果: 八字={v.get('bazi_confidence')}, 紫微={v.get('ziwei_confidence')}")
            except Exception as e:
                print(f"⚠️ 获取验证结果失败: {e}")
        
        # 获取Primary AI的系统Prompt（动态加载最新问卷 + 注入 Child AI 验证结果）
        system_prompt = get_primary_ai_prompt(bazi_result=bazi_result, ziwei_result=ziwei_result)
        
        # 【知识检索增强】Primary AI 使用规则 + 模式
        knowledge_context = ""
        if KNOWLEDGE_AVAILABLE and user_message and find_relevant_knowledge and allow_access:
            try:
                results = find_relevant_knowledge(user_message)
                if results:
                    knowledge_parts = ["【命理知识参考】"]
                    for ktype, fname, content in results:
                        if allow_access("primary", ktype):
                            if ktype == "rule":
                                knowledge_parts.append(f"- 规则({fname}): {str(content)[:150]}...")
                            elif ktype == "pattern":
                                knowledge_parts.append(f"- 统计规律({fname}): {json.dumps(content, ensure_ascii=False)[:150]}...")
                    
                    if len(knowledge_parts) > 1:
                        knowledge_context = "\n".join(knowledge_parts) + "\n\n"
                        print(f"✅ Primary AI 知识库增强: {len(results)} 条匹配")
            except Exception as e:
                print(f"⚠️ 知识检索失败: {e}")
        
        # 获取命盘上下文
        primary_context = get_primary_context(user_id)
        
        # 构建消息列表
        messages = [{"role": "system", "content": system_prompt + "\n\n" + primary_context}]
        
        # 添加历史对话（最多保留最近10轮）
        if conversation_history:
            messages.extend(conversation_history[-20:])  # 保留最近20条消息（10轮对话）
        
        # 添加当前用户消息（带知识库增强）
        enhanced_message = f"{knowledge_context}{user_message}" if knowledge_context else user_message
        messages.append({"role": "user", "content": enhanced_message})
        
        # 调用OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        ai_reply = (response.choices[0].message.content or "").strip()
        
        # 【Child AI 智能提示】在验证触发之前，先让子AI提供更聪明的提问建议
        # 获取已上传命盘数据
        bazi_chart, ziwei_chart = get_current_uploaded_charts(user_id)
        
        # 调用子AI提示（child ai 不自行发言，仅提供暗示）
        try:
            # 构建对话记忆（最近的对话内容）
            conversation_memory = "\n".join([
                f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" 
                for msg in conversation_history[-10:] if msg.get('content')
            ])
            
            hint_result = generate_child_ai_hint(bazi_chart, ziwei_chart, conversation_memory)
            
            # 尝试解析 hint 结果
            if hint_result:
                try:
                    hint = json.loads(hint_result)
                    if hint.get("should_ask") and hint.get("suggested_question"):
                        # 使用 Child AI 建议的问题替代 Primary AI 的回答
                        ai_reply = hint["suggested_question"]
                        print(f"✅ Child AI 提供智能提示，引导更深入对话")
                except json.JSONDecodeError:
                    print(f"⚠️ Child AI hint 解析失败，使用原始 Primary AI 回答")
        except Exception as hint_error:
            print(f"⚠️ Child AI hint 生成失败: {hint_error}")
        
        # 检测是否触发验证
        trigger_verification = False
        completion_keywords = ["完成", "验证一下", "我讲完了", "验证", "开始验证", "帮我验证"]
        
        if chart_uploaded and life_events and any(keyword in user_message for keyword in completion_keywords):
            # 检查人生事件是否至少有3条
            life_events_count = len([line for line in life_events.split('\n') if line.strip()]) if life_events else 0
            
            if life_events_count >= 3:
                trigger_verification = True
                
                # 执行双子AI验证
                try:
                    print(f"🔍 触发AI验证: user_id={user_id}, group={group_index}, events={life_events_count}条")
                    
                    bazi_result = asyncio.run(verify_chart_with_ai(parsed_chart, life_events, "bazi", bazi_name))
                    ziwei_result = asyncio.run(verify_chart_with_ai(parsed_chart, life_events, "ziwei", ziwei_name))
                    
                    # 存储验证结果
                    if sp:
                        save_verification_results(
                            user_id=user_id,
                            group_index=group_index,
                            bazi_result=bazi_result,
                            ziwei_result=ziwei_result,
                            life_events_count=life_events_count,
                            sp=sp
                        )
                    
                    # 返回带验证结果的响应
                    return jsonify({
                        "ok": True,
                        "message": ai_reply,
                        "ai_name": primary_ai_name,
                        "verification_triggered": True,
                        "bazi_verification": bazi_result,
                        "ziwei_verification": ziwei_result
                    })
                    
                except Exception as verify_error:
                    print(f"❌ 验证失败: {verify_error}")
                    # 验证失败时仍返回对话，但提示验证失败
                    return jsonify({
                        "ok": True,
                        "message": ai_reply + "\n\n抱歉，命盘验证遇到了一些问题，请稍后再试。",
                        "ai_name": primary_ai_name,
                        "verification_triggered": False,
                        "verification_error": str(verify_error)
                    })
        
        # 检查是否已锁定真命盘（这里简化处理，实际应该从数据库或session获取）
        chart_locked = data.get("chart_locked", False)
        
        # 格式化AI响应，如果已锁定命盘则添加验证按钮
        formatted_reply = format_ai_response(ai_reply, chart_locked)
        
        # 正常对话响应
        return jsonify({
            "ok": True,
            "message": formatted_reply,
            "ai_name": primary_ai_name,
            "verification_triggered": False,
            "chart_locked": chart_locked
        })
    
    except Exception as e:
        print(f"❌ Primary AI 对话失败: {e}")
        return jsonify({
            "ok": False,
            "message": f"抱歉，我现在有些不舒服，请稍后再试。（{str(e)}）"
        }), 500


@bp.post("/api/validation_log")
def log_validation():
    """
    记录用户对命理断语的验证结果
    """
    if not sp:
        return jsonify({
            "ok": False,
            "toast": "数据库未配置，无法记录验证结果"
        }), 500
    
    data = request.json or {}
    
    user_id = data.get("user_id")
    chart_id = data.get("chart_id")
    click_data = data.get("click_data")  # 格式: "#yes-STATEMENT_ID" 或 "#no-STATEMENT_ID"
    ai_statement = data.get("ai_statement", "")
    source_ai = data.get("source_ai", "Primary")
    
    if not user_id or not chart_id or not click_data:
        return jsonify({
            "ok": False,
            "toast": "缺少必要参数"
        }), 400
    
    # 解析点击数据
    click_result = parse_validation_click(click_data)
    if not click_result.get("valid"):
        return jsonify({
            "ok": False,
            "toast": "无效的点击数据格式"
        }), 400
    
    statement_id = click_result["statement_id"]
    user_choice = click_result["user_choice"]
    
    try:
        # 创建验证日志
        validation_log = create_validation_log(
            user_id=user_id,
            chart_id=chart_id,
            statement_id=statement_id,
            ai_statement=ai_statement,
            user_choice=user_choice,
            source_ai=source_ai
        )
        
        # 写入数据库
        result = sp.table("truth_validation_logs").insert(validation_log).execute()
        
        if result.data:
            # 调用Child AI进行实时验证
            try:
                from verify.ai_verifier import verify_chart_with_ai
                import asyncio
                
                # 获取命盘数据进行验证
                chart_data = sp.table("verified_charts").select("parsed").eq("id", chart_id).execute()
                if chart_data.data:
                    parsed_chart = chart_data.data[0].get("parsed", {})
                    
                    # 生成验证提示
                    verification_prompt = f"请验证以下断语是否准确：{ai_statement}"
                    
                    # 调用Child AI验证
                    ai_verification = asyncio.run(verify_chart_with_ai(
                        parsed_chart,
                        verification_prompt,
                        "ziwei" if "紫微" in source_ai else "bazi",
                        source_ai
                    ))
                    
                    return jsonify({
                        "ok": True,
                        "toast": "验证结果已记录",
                        "log_id": result.data[0]["id"],
                        "ai_verification": ai_verification
                    })
            except Exception as verify_error:
                print(f"⚠️ Child AI验证失败: {verify_error}")
                # 即使验证失败，也返回成功，因为日志已记录
            
            return jsonify({
                "ok": True,
                "toast": "验证结果已记录",
                "log_id": result.data[0]["id"]
            })
        
    except Exception as e:
        print(f"❌ 记录验证结果失败: {e}")
        return jsonify({
            "ok": False,
            "toast": f"记录验证结果失败：{str(e)}"
        }), 500


@bp.post("/api/confirm_true_chart")
def confirm_true_chart():
    """
    用户确认真命盘，启用验证模式
    """
    if not sp:
        return jsonify({
            "ok": False,
            "toast": "数据库未配置"
        }), 500
    
    data = request.json or {}
    
    user_id = data.get("user_id")
    chart_id = data.get("chart_id")
    
    if not user_id or not chart_id:
        return jsonify({
            "ok": False,
            "toast": "缺少用户ID或命盘ID"
        }), 400
    
    try:
        # 更新用户状态，标记已锁定真命盘
        # 这里假设有一个user_status表来存储用户状态
        # 如果没有，可以使用session或其他方式
        
        print(f"[System] 用户锁定真命盘 {chart_id}")
        
        return jsonify({
            "ok": True,
            "toast": "真命盘已确认，现在可以开始验证断语",
            "chart_locked": True
        })
        
    except Exception as e:
        return jsonify({
            "ok": False,
            "toast": f"确认真命盘失败：{str(e)}"
        }), 500