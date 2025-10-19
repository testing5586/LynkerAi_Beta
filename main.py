# ============================================================
# Lynker Master AI 主控引擎
# ============================================================

import os
import json
from datetime import datetime
from supabase_init import init_supabase
from ai_truechart_verifier import run_truechart_verifier

# 预留未来模块接口
# from guru_apprentice import run_guru_apprentice
from soulmate_matcher import run_soulmate_matcher
from child_ai_insight import run_child_ai_insight

def log_event(event_type, data):
    """统一日志记录"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {"time": timestamp, "type": event_type, "data": data}
    with open("master_log.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    print(f"🪶 Logged event → {event_type}")

def main():
    print("🚀 Starting Lynker Master AI Engine ...")

    # 初始化 Supabase
    supabase = init_supabase()
    if supabase is None:
        print("⚠️ Supabase 连接失败，仅本地运行。")

    # 用户身份示例
    user_id = os.getenv("LYNKER_USER_ID", "u_demo")

    # 启动命盘验证模块
    print("\n🔍 [1] 正在执行真命盘验证模块...")
    verifier_result = run_truechart_verifier(user_id, supabase_client=supabase)
    log_event("truechart_verification", verifier_result)

    # 启动同命匹配模块
    print("\n💞 [2] 启动同命匹配模块...")
    match_result = run_soulmate_matcher(user_id, supabase)
    log_event("soulmate_matching", match_result)

    # 启动子AI洞察生成模块
    print("\n🤖 [3] 启动子AI洞察生成模块...")
    if match_result and isinstance(match_result, dict) and match_result.get("matches"):
        insight_result = run_child_ai_insight(user_id, match_result["matches"], supabase)
        log_event("child_ai_insights", insight_result)
    else:
        print("⚠️ 无匹配结果，跳过子AI洞察生成。")

    print("\n✅ Lynker Master AI 完成所有模块任务。")

if __name__ == "__main__":
    main()
