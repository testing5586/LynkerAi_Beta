"""
Mode B - 灵伴主导式全盘验证机制 Flask 路由
Companion-Led Full Chart Verification Mode Routes

核心功能：
1. 导入八字与紫微命盘 JSON
2. 选择 SOP 分析模板
3. 并行调用八字与紫微 Child AI
4. 生成 Primary AI 综合总结
5. 存储验证日志到数据库
"""

import os
import json
import asyncio
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, session
from supabase import create_client

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from verify.ai_verifier import verify_chart_with_ai
from verify.ai_prompts import get_ai_names_from_db

bp = Blueprint("full_chart_verify", __name__, url_prefix="/verify")

# 初始化 Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
sp = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# ======================
# SOP 模板管理目录
# ======================
SOP_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "sop_templates")
os.makedirs(SOP_TEMPLATE_DIR, exist_ok=True)


def load_sop_template(template_id):
    """
    加载 SOP 分析模板

    Args:
        template_id: 模板ID，例如 "standard_v1"

    Returns:
        dict: SOP 模板内容
    """
    template_file = os.path.join(SOP_TEMPLATE_DIR, f"{template_id}.json")

    if not os.path.exists(template_file):
        # 返回默认模板
        return get_default_sop_template()

    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 加载 SOP 模板失败: {e}")
        return get_default_sop_template()


def get_default_sop_template():
    """
    获取默认 SOP 模板（标准全盘分析 v1.0）

    Returns:
        dict: 默认模板结构
    """
    return {
        "template_id": "standard_v1",
        "template_name": "标准全盘分析 v1.0",
        "modules": [
            {
                "module_id": "family",
                "module_name": "六亲关系",
                "description": "分析父母、兄弟姐妹、子女关系",
                "weight": 1.0
            },
            {
                "module_id": "childhood",
                "module_name": "童年经历",
                "description": "分析0-18岁成长环境与重要事件",
                "weight": 1.0
            },
            {
                "module_id": "major_events",
                "module_name": "重大事件",
                "description": "分析人生转折点、意外事件、重要决策",
                "weight": 1.5
            },
            {
                "module_id": "relationships",
                "module_name": "感情婚姻",
                "description": "分析恋爱、婚姻、伴侣关系",
                "weight": 1.2
            },
            {
                "module_id": "career",
                "module_name": "事业财运",
                "description": "分析职业发展、财富积累、事业成就",
                "weight": 1.2
            },
            {
                "module_id": "health",
                "module_name": "健康状况",
                "description": "分析身体健康、疾病史、体质特征",
                "weight": 1.0
            }
        ]
    }


def save_sop_template(template_data):
    """
    保存自定义 SOP 模板

    Args:
        template_data: dict，包含 template_id 和完整模板内容

    Returns:
        bool: 保存是否成功
    """
    template_id = template_data.get("template_id")
    if not template_id:
        return False

    template_file = os.path.join(SOP_TEMPLATE_DIR, f"{template_id}.json")

    try:
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, ensure_ascii=False, indent=2)
        print(f"✅ SOP 模板已保存: {template_id}")
        return True
    except Exception as e:
        print(f"❌ 保存 SOP 模板失败: {e}")
        return False


# ======================
# 并行调用 Child AI
# ======================

async def run_bazi_analysis(bazi_chart, sop_template, ai_name="八字观察员"):
    """
    运行八字 Child AI 分析

    Args:
        bazi_chart: dict，八字命盘数据
        sop_template: dict，SOP 分析模板
        ai_name: str，八字 AI 名称

    Returns:
        dict: 八字分析结果，包含各模块的分析内容
    """
    try:
        # 构建分析上下文
        modules = sop_template.get("modules", [])
        context = f"请依据以下命盘进行全面分析：\n{json.dumps(bazi_chart, ensure_ascii=False)}\n\n"
        context += "分析模块：\n"

        for module in modules:
            context += f"- {module['module_name']}: {module['description']}\n"

        # 调用八字 Child AI
        print(f"🔍 [八字 AI] 开始分析...")
        result = await verify_chart_with_ai(bazi_chart, context, "bazi", ai_name)

        # 解析结果并按模块组织
        module_results = []
        for module in modules:
            module_result = {
                "module_id": module["module_id"],
                "module_name": module["module_name"],
                "summary": result.get("summary", ""),
                "confidence": result.get("birth_time_confidence", "中"),
                "supporting_evidence": result.get("key_supporting_evidence", []),
                "conflicts": result.get("key_conflicts", [])
            }
            module_results.append(module_result)

        print(f"✅ [八字 AI] 分析完成，置信度: {result.get('birth_time_confidence', '中')}")

        return {
            "ok": True,
            "ai_name": ai_name,
            "overall_confidence": result.get("birth_time_confidence", "中"),
            "modules": module_results,
            "raw_result": result
        }

    except Exception as e:
        print(f"❌ [八字 AI] 分析失败: {e}")
        return {
            "ok": False,
            "error": str(e),
            "ai_name": ai_name,
            "modules": []
        }


async def run_ziwei_analysis(ziwei_chart, sop_template, ai_name="星盘参谋"):
    """
    运行紫微 Child AI 分析

    Args:
        ziwei_chart: dict，紫微命盘数据
        sop_template: dict，SOP 分析模板
        ai_name: str，紫微 AI 名称

    Returns:
        dict: 紫微分析结果，包含各模块的分析内容
    """
    try:
        # 构建分析上下文
        modules = sop_template.get("modules", [])
        context = f"请依据以下命盘进行全面分析：\n{json.dumps(ziwei_chart, ensure_ascii=False)}\n\n"
        context += "分析模块：\n"

        for module in modules:
            context += f"- {module['module_name']}: {module['description']}\n"

        # 调用紫微 Child AI
        print(f"🔮 [紫微 AI] 开始分析...")
        result = await verify_chart_with_ai(ziwei_chart, context, "ziwei", ai_name)

        # 解析结果并按模块组织
        module_results = []
        for module in modules:
            module_result = {
                "module_id": module["module_id"],
                "module_name": module["module_name"],
                "summary": result.get("summary", ""),
                "confidence": result.get("birth_time_confidence", "中"),
                "supporting_evidence": result.get("key_supporting_evidence", []),
                "conflicts": result.get("key_conflicts", [])
            }
            module_results.append(module_result)

        print(f"✅ [紫微 AI] 分析完成，置信度: {result.get('birth_time_confidence', '中')}")

        return {
            "ok": True,
            "ai_name": ai_name,
            "overall_confidence": result.get("birth_time_confidence", "中"),
            "modules": module_results,
            "raw_result": result
        }

    except Exception as e:
        print(f"❌ [紫微 AI] 分析失败: {e}")
        return {
            "ok": False,
            "error": str(e),
            "ai_name": ai_name,
            "modules": []
        }


async def run_parallel_analysis(bazi_chart, ziwei_chart, sop_template, bazi_name="八字观察员", ziwei_name="星盘参谋"):
    """
    并行运行八字和紫微 Child AI 分析

    Args:
        bazi_chart: dict，八字命盘数据
        ziwei_chart: dict，紫微命盘数据
        sop_template: dict，SOP 分析模板
        bazi_name: str，八字 AI 名称
        ziwei_name: str，紫微 AI 名称

    Returns:
        tuple: (bazi_result, ziwei_result)
    """
    print(f"🚀 [并行分析] 启动八字与紫微 AI 并行分析...")

    # 使用 asyncio.gather 并行执行
    bazi_task = run_bazi_analysis(bazi_chart, sop_template, bazi_name)
    ziwei_task = run_ziwei_analysis(ziwei_chart, sop_template, ziwei_name)

    bazi_result, ziwei_result = await asyncio.gather(bazi_task, ziwei_task)

    print(f"✅ [并行分析] 双 AI 分析完成")

    return bazi_result, ziwei_result


# ======================
# Primary AI 综合总结
# ======================

def generate_primary_ai_summary(bazi_result, ziwei_result, sop_template):
    """
    生成 Primary AI 综合总结

    Args:
        bazi_result: dict，八字分析结果
        ziwei_result: dict，紫微分析结果
        sop_template: dict，SOP 分析模板

    Returns:
        dict: Primary AI 总结，包含一致性分析和建议
    """
    try:
        from openai import OpenAI

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or os.getenv("LYNKER_MASTER_KEY"))

        if not client.api_key:
            return {
                "ok": False,
                "error": "OpenAI API Key 未配置"
            }

        # 构建 Primary AI Prompt
        prompt = f"""你是灵伴 AI，负责综合分析八字与紫微两个系统的验证结果。

【八字分析结果】
置信度: {bazi_result.get('overall_confidence', '未知')}
{json.dumps(bazi_result.get('modules', []), ensure_ascii=False, indent=2)}

【紫微分析结果】
置信度: {ziwei_result.get('overall_confidence', '未知')}
{json.dumps(ziwei_result.get('modules', []), ensure_ascii=False, indent=2)}

请从以下角度进行综合分析：

1. **一致性评分** (0-100分)：八字与紫微的结论有多少一致之处？
2. **核心一致点**：两个系统在哪些模块上得出了相似结论？
3. **主要分歧点**：两个系统在哪些模块上存在明显差异？
4. **可信度评估**：综合两个系统的结果，这个出生时辰的可信度如何？
5. **下一步建议**：用户应该关注哪些方面来进一步验证？

请以 JSON 格式返回：
{{
    "consistency_score": 85,
    "consistent_points": ["六亲关系", "事业财运"],
    "divergent_points": ["感情婚姻"],
    "credibility_assessment": "高",
    "next_steps": ["建议进一步核实感情经历细节"],
    "summary_text": "综合八字与紫微的分析..."
}}
"""

        print(f"🧠 [Primary AI] 正在生成综合总结...")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是专业的命理分析专家，擅长综合多个系统的分析结果。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        summary_text = response.choices[0].message.content.strip()

        # 尝试解析 JSON
        try:
            summary_data = json.loads(summary_text)
            print(f"✅ [Primary AI] 总结生成完成，一致性评分: {summary_data.get('consistency_score', 0)}")
            return {
                "ok": True,
                "data": summary_data
            }
        except json.JSONDecodeError:
            # 如果无法解析 JSON，返回原始文本
            print(f"⚠️ [Primary AI] 无法解析 JSON，返回原始文本")
            return {
                "ok": True,
                "data": {
                    "consistency_score": 50,
                    "summary_text": summary_text
                }
            }

    except Exception as e:
        print(f"❌ [Primary AI] 总结生成失败: {e}")
        return {
            "ok": False,
            "error": str(e)
        }


# ======================
# 数据库存储
# ======================

def save_verification_log(user_id, mode, bazi_result, ziwei_result, primary_summary, sop_template_id):
    """
    保存验证日志到数据库

    Args:
        user_id: 用户ID
        mode: 验证模式 ("full_chart")
        bazi_result: 八字分析结果
        ziwei_result: 紫微分析结果
        primary_summary: Primary AI 总结
        sop_template_id: SOP 模板ID

    Returns:
        int: 日志ID，失败返回 None
    """
    if not sp:
        print("⚠️ 数据库未配置，无法保存验证日志")
        return None

    try:
        log_data = {
            "user_id": int(user_id),
            "mode": mode,
            "sop_template_id": sop_template_id,
            "bazi_confidence": bazi_result.get("overall_confidence", "未知"),
            "bazi_modules": json.dumps(bazi_result.get("modules", []), ensure_ascii=False),
            "ziwei_confidence": ziwei_result.get("overall_confidence", "未知"),
            "ziwei_modules": json.dumps(ziwei_result.get("modules", []), ensure_ascii=False),
            "consistency_score": primary_summary.get("consistency_score", 0),
            "primary_summary": json.dumps(primary_summary, ensure_ascii=False),
            "created_at": datetime.now().isoformat()
        }

        result = sp.table("verification_logs").insert(log_data).execute()

        if result.data and len(result.data) > 0:
            log_id = result.data[0].get("id")
            print(f"✅ 验证日志已保存: log_id={log_id}")
            return log_id
        else:
            print("❌ 保存验证日志失败：无返回数据")
            return None

    except Exception as e:
        print(f"❌ 保存验证日志失败: {e}")
        return None


# ======================
# Flask 路由
# ======================

@bp.get("/full_chart")
def render_full_chart_page():
    """
    渲染 Mode B 全盘验证页面
    """
    user_id = session.get("user_id") or request.args.get("user_id")

    if not user_id:
        return jsonify({
            "ok": False,
            "toast": "请先登录后再使用全盘验证功能"
        }), 401

    return render_template("full_chart_verification.html", user_id=user_id)


@bp.get("/api/sop_templates")
def list_sop_templates():
    """
    列出所有可用的 SOP 模板

    Returns:
        JSON: 模板列表
    """
    try:
        templates = []

        # 扫描 SOP 模板目录
        if os.path.exists(SOP_TEMPLATE_DIR):
            for filename in os.listdir(SOP_TEMPLATE_DIR):
                if filename.endswith(".json"):
                    template_id = filename[:-5]  # 移除 .json 后缀
                    template = load_sop_template(template_id)
                    templates.append({
                        "id": template_id,
                        "name": template.get("template_name", template_id)
                    })

        # 添加默认模板
        if not templates:
            templates = [
                {"id": "standard_v1", "name": "标准全盘分析 v1.0"},
                {"id": "career_focused_v1", "name": "事业重点分析 v1.0"},
                {"id": "relationship_focused_v1", "name": "感情重点分析 v1.0"}
            ]

        return jsonify({
            "ok": True,
            "templates": templates
        })

    except Exception as e:
        print(f"❌ 获取 SOP 模板列表失败: {e}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500


@bp.post("/api/upload_sop")
def upload_custom_sop():
    """
    上传自定义 SOP 模板

    接收：
        - file: JSON 文件

    返回：
        - template_id: 新模板的ID
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                "ok": False,
                "toast": "未检测到上传的文件"
            }), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({
                "ok": False,
                "toast": "文件名为空"
            }), 400

        # 读取并解析 JSON
        content = file.read()
        template_data = json.loads(content)

        # 验证模板格式
        if "template_id" not in template_data or "modules" not in template_data:
            return jsonify({
                "ok": False,
                "toast": "模板格式错误：缺少 template_id 或 modules"
            }), 400

        # 保存模板
        success = save_sop_template(template_data)

        if success:
            return jsonify({
                "ok": True,
                "template_id": template_data["template_id"],
                "toast": f"模板 {template_data.get('template_name', '')} 上传成功"
            })
        else:
            return jsonify({
                "ok": False,
                "toast": "模板保存失败"
            }), 500

    except json.JSONDecodeError:
        return jsonify({
            "ok": False,
            "toast": "文件格式错误：无法解析 JSON"
        }), 400
    except Exception as e:
        print(f"❌ 上传 SOP 模板失败: {e}")
        return jsonify({
            "ok": False,
            "toast": f"上传失败：{str(e)}"
        }), 500


@bp.post("/api/run_full_chart_ai")
def run_full_chart_analysis():
    """
    ⚠️ 核心接口：运行 Mode B 全盘验证分析

    接收：
        - mode: "full_chart"
        - sop_template_id: SOP 模板ID
        - bazi_chart: 八字命盘 JSON
        - ziwei_chart: 紫微命盘 JSON
        - user_id: 用户ID
        - lang: 语言 (默认 "zh")

    返回：
        - bazi_analysis: 八字分析结果
        - ziwei_analysis: 紫微分析结果
        - primary_ai_summary: Primary AI 综合总结
        - consistency_score: 一致性评分
        - log_id: 验证日志ID
    """

    data = request.json or {}

    # ========== 1. 参数验证 ==========
    mode = data.get("mode")
    sop_template_id = data.get("sop_template_id")
    bazi_chart = data.get("bazi_chart")
    ziwei_chart = data.get("ziwei_chart")
    user_id = data.get("user_id")
    lang = data.get("lang", "zh")

    if mode != "full_chart":
        return jsonify({
            "ok": False,
            "toast": "无效的模式，应为 'full_chart'"
        }), 400

    if not sop_template_id:
        return jsonify({
            "ok": False,
            "toast": "请选择 SOP 分析模板"
        }), 400

    if not bazi_chart or not ziwei_chart:
        return jsonify({
            "ok": False,
            "toast": "请先导入八字与紫微命盘"
        }), 400

    if not user_id:
        return jsonify({
            "ok": False,
            "toast": "缺少用户ID"
        }), 400

    # ========== 2. 加载 SOP 模板 ==========
    print(f"📋 [Mode B] 加载 SOP 模板: {sop_template_id}")
    sop_template = load_sop_template(sop_template_id)

    # ========== 3. 获取 Child AI 名称 ==========
    bazi_name = "八字观察员"
    ziwei_name = "星盘参谋"

    if sp:
        try:
            ai_names = get_ai_names_from_db(user_id, sp)
            if ai_names:
                bazi_name = ai_names.get("bazi", "八字观察员")
                ziwei_name = ai_names.get("ziwei", "星盘参谋")
        except Exception as e:
            print(f"⚠️ 获取 AI 名称失败，使用默认值: {e}")

    # ========== 4. 并行调用 Child AI 分析 ==========
    try:
        print(f"🚀 [Mode B] 开始并行分析: user_id={user_id}")

        # 使用 asyncio.run 执行并行分析
        bazi_result, ziwei_result = asyncio.run(
            run_parallel_analysis(bazi_chart, ziwei_chart, sop_template, bazi_name, ziwei_name)
        )

        # 检查分析是否成功
        if not bazi_result.get("ok") or not ziwei_result.get("ok"):
            error_msg = []
            if not bazi_result.get("ok"):
                error_msg.append(f"八字分析失败: {bazi_result.get('error', '未知错误')}")
            if not ziwei_result.get("ok"):
                error_msg.append(f"紫微分析失败: {ziwei_result.get('error', '未知错误')}")

            return jsonify({
                "ok": False,
                "toast": "；".join(error_msg)
            }), 500

        # ========== 5. 生成 Primary AI 综合总结 ==========
        print(f"🧠 [Mode B] 生成 Primary AI 总结")

        primary_summary_result = generate_primary_ai_summary(bazi_result, ziwei_result, sop_template)

        if not primary_summary_result.get("ok"):
            return jsonify({
                "ok": False,
                "toast": f"Primary AI 总结生成失败: {primary_summary_result.get('error', '未知错误')}"
            }), 500

        primary_summary = primary_summary_result["data"]

        # ========== 6. 存储验证日志 ==========
        print(f"💾 [Mode B] 保存验证日志")

        log_id = save_verification_log(
            user_id=user_id,
            mode=mode,
            bazi_result=bazi_result,
            ziwei_result=ziwei_result,
            primary_summary=primary_summary,
            sop_template_id=sop_template_id
        )

        # ========== 7. 返回结果 ==========
        print(f"✅ [Mode B] 全盘验证完成: log_id={log_id}, consistency_score={primary_summary.get('consistency_score', 0)}")

        return jsonify({
            "ok": True,
            "data": {
                "bazi_analysis": bazi_result,
                "ziwei_analysis": ziwei_result,
                "primary_ai_summary": primary_summary,
                "consistency_score": primary_summary.get("consistency_score", 0),
                "log_id": log_id
            },
            "toast": f"全盘验证完成！一致性评分: {primary_summary.get('consistency_score', 0)}/100"
        })

    except Exception as e:
        print(f"❌ [Mode B] 全盘验证失败: {e}")
        import traceback
        traceback.print_exc()

        return jsonify({
            "ok": False,
            "toast": f"分析失败：{str(e)}"
        }), 500


# ======================
# 调试接口
# ======================

@bp.get("/api/test_parallel")
def test_parallel_analysis():
    """
    测试并行分析功能（开发调试用）
    """
    # 模拟命盘数据
    bazi_chart = {
        "year_pillar": "甲子",
        "month_pillar": "丙寅",
        "day_pillar": "戊午",
        "hour_pillar": "庚申"
    }

    ziwei_chart = {
        "main_palace": "命宫",
        "main_stars": ["紫微", "天府"],
        "wealth_palace": "财帛宫"
    }

    sop_template = get_default_sop_template()

    try:
        bazi_result, ziwei_result = asyncio.run(
            run_parallel_analysis(bazi_chart, ziwei_chart, sop_template)
        )

        return jsonify({
            "ok": True,
            "bazi_result": bazi_result,
            "ziwei_result": ziwei_result
        })

    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500
