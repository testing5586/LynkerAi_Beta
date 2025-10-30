"""
Group Leader 模块
Lynker Engine v2.0
连接层：Child AI → Group Leader → Master AI
功能：
- 收集各 Child AI 输出
- 格式化 / 合并
- 传递给 Master AI 进行深度推理
"""

import datetime
import json
import sys
import os
try:
    from .master_ai import run_master_ai
except ImportError:
    from lynker_engine.core.master_ai import run_master_ai

# Set console encoding for Windows
if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# ========== 🔹 工具函数 ==========
def safe_log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] GroupLeader> {msg}")

def safe_json(obj):
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except:
        return str(obj)

# ========== 🔹 主函数入口 ==========
def run_group_leader(task_topic, child_outputs):
    """
    task_topic: str - 任务主题，例如 "对照分析：天府 vs 武曲"
    child_outputs: dict - 子 AI 的输出合集，例如：
    {
      "bazi_child": {...},
      "ziwei_child": {...},
      "tarot_child": {...}
    }
    """

    safe_log(f"接收到任务: {task_topic}")
    safe_log(f"子 AI 输出摘要: {list(child_outputs.keys())}")

    # Step 1️⃣: 数据清洗
    normalized = normalize_child_outputs(child_outputs)

    # Step 2️⃣: 生成协调报告
    notes = summarize_alignment(normalized)

    # Step 3️⃣: 打包任务 → 交给 Master AI
    payload = {
        "topic": task_topic,
        "bazi_result": normalized.get("bazi_child"),
        "ziwei_result": normalized.get("ziwei_child"),
        "tarot_result": normalized.get("tarot_child"),
        "group_notes": notes
    }

    safe_log("已打包任务，传递给 Master AI ...")
    master_output = run_master_ai(payload)

    # Step 4️⃣: 输出最终结果
    safe_log("Master AI 已返回结果 ✅")
    return {
        "group_notes": notes,
        "master_result": master_output
    }


# ========== 🔹 辅助 1：统一子 AI 输出格式 ==========
def normalize_child_outputs(outputs):
    """
    将不同子 AI 的输出标准化为统一 JSON 格式
    """
    normalized = {}
    for name, data in outputs.items():
        if not data:
            continue
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except:
                data = {"summary": data}
        normalized[name] = {
            "birth_time_confidence": data.get("birth_time_confidence", "未知"),
            "key_supporting_evidence": data.get("key_supporting_evidence", []),
            "key_conflicts": data.get("key_conflicts", []),
            "summary": data.get("summary", "无摘要")
        }
    return normalized


# ========== 🔹 辅助 2：生成协调报告 ==========
def summarize_alignment(normalized):
    """
    汇总不同命盘验证结果的总体趋势
    """
    notes = []
    for name, result in normalized.items():
        conf = result.get("birth_time_confidence", "未知")
        summary = result.get("summary", "")
        notes.append(f"{name} 可信度：{conf} → {summary}")
    if not notes:
        return "暂无子 AI 输出。"
    return " | ".join(notes)


# ========== 🔹 测试入口 ==========
if __name__ == "__main__":
    # 模拟两个子 AI 输出
    child_outputs = {
        "bazi_child": {
            "birth_time_confidence": "高",
            "key_supporting_evidence": ["事业线与真实经历吻合"],
            "key_conflicts": ["婚期略早于命盘显示"],
            "summary": "整体吻合度高"
        },
        "ziwei_child": {
            "birth_time_confidence": "中高",
            "key_supporting_evidence": ["命宫主星特质一致"],
            "key_conflicts": [],
            "summary": "总体准确"
        }
    }

    print(safe_json(run_group_leader("对照分析：天府 vs 武曲", child_outputs)))