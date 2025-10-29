"""
Superintendent 控制模块（数据库版）
Lynker Engine v2.3
------------------------------------------------
自动读取最新的八字与紫微命盘验证结果，
支持 chart_type 字段自动识别八字/紫微类型，
协调 Group Leader 与 Master AI 完成推理报告。
"""

import datetime
import json
import sys
import os
from supabase import create_client, Client
from .group_leader import run_group_leader
from .master_ai import run_master_ai

# Set console encoding for Windows
if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# ========== 🔹 Supabase 初始化 ==========
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='../../.env')
load_dotenv(dotenv_path='.env')
load_dotenv()

def init_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        print(f"[{timestamp()}] ⚠️ 警告：未找到 Supabase 环境变量，使用模拟模式")
        return None
    return create_client(url, key)

# ========== 🔹 工具函数 ==========
def timestamp():
    return datetime.datetime.now().strftime("%H:%M:%S")

def safe_json(obj):
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except:
        return str(obj)

# ========== 🔹 数据读取 ==========
def fetch_latest_verification(supabase: Client, user_id: str):
    try:
        res = (
            supabase.table("verified_charts")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(5)   # 允许多条，便于识别八字/紫微
            .execute()
        )
        if res.data:
            print(f"[{timestamp()}] 🗂 已读取 {len(res.data)} 条验证记录")
            return res.data
        else:
            print(f"[{timestamp()}] ⚠️ 未找到任何验证记录。")
    except Exception as e:
        print(f"[{timestamp()}] ❌ 读取失败: {e}")
    return []

def classify_charts(records):
    """自动判断命盘类型"""
    bazi, ziwei = None, None
    for rec in records:
        chart_type = rec.get("chart_type") or ""
        if "八字" in chart_type or chart_type.lower().startswith("b"):
            bazi = rec
        elif "紫微" in chart_type or chart_type.lower().startswith("z"):
            ziwei = rec
    if not bazi and records:
        bazi = records[0]
    if not ziwei and len(records) > 1:
        ziwei = records[1]
    return bazi, ziwei

def build_chart_result(rec, label):
    """统一格式化结果"""
    return {
        "birth_time_confidence": rec.get("confidence", "中"),
        "key_supporting_evidence": rec.get("matched_keywords", []),
        "summary": f"{label}验证记录：{rec.get('score', 0):.2f} 分"
    }

# ========== 🔹 主执行逻辑 ==========
def run_superintendent_db(user_id: str, task_topic: str):
    print("=" * 70)
    print(f"[{timestamp()}] ✅ 系统: Lynker Engine v2.3（多命盘自动识别模式）已启动...")
    print(f"[{timestamp()}] 👤 Superintendent> 任务主题: {task_topic}")

    supabase = init_supabase()
    records = fetch_latest_verification(supabase, user_id)
    if not records:
        print(f"[{timestamp()}] ❌ 无法继续：未找到用户 {user_id} 的命盘数据。")
        return None

    # 🔍 自动区分八字 / 紫微
    bazi_rec, ziwei_rec = classify_charts(records)
    if not bazi_rec:
        bazi_rec = records[0]
    if not ziwei_rec:
        ziwei_rec = bazi_rec

    bazi_result = build_chart_result(bazi_rec, "八字")
    ziwei_result = build_chart_result(ziwei_rec, "紫微")

    print(f"[{timestamp()}] 🧩 Group Leader> 整合两命盘结果中...")
    group_result = run_group_leader(task_topic, {
        "bazi_child": bazi_result,
        "ziwei_child": ziwei_result
    })

    print(f"[{timestamp()}] 🧠 Master AI> 启动深度推理...")
    master_result = run_master_ai({
        "topic": task_topic,
        "bazi_result": bazi_result,
        "ziwei_result": ziwei_result,
        "group_notes": group_result.get("group_notes", [])
    })

    print(f"[{timestamp()}] 📊 最终报告:\n{json.dumps(master_result, ensure_ascii=False, indent=2)}")
    print("=" * 70)
    print(f"[{timestamp()}] 🏁 任务完成。")
    return master_result


# ========== 🔹 测试入口 ==========
if __name__ == "__main__":
    test_user_id = "u_demo"   # ✅ 使用已存在的用户ID
    test_topic = "验证天府坐命与武曲守财命盘的真实度与预期差异"
    run_superintendent_db(test_user_id, test_topic)
