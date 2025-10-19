# ==========================================================
# LynkerAI TrueChart Verifier v1.0
# 功能：验证用户导入的命盘与人生轨迹吻合度，并生成 life_tags
# 作者：GPT-5（协同 Kynn）
# 日期：2025-10-19
# ==========================================================

import json
import os
from datetime import datetime
from difflib import SequenceMatcher

# ----------------------------------------------------------------
# 辅助函数
# ----------------------------------------------------------------
def similarity(a, b):
    """模糊匹配计算两句文字的相似度"""
    return SequenceMatcher(None, a, b).ratio()


def fuzzy_match(text, keywords):
    """判断文本中是否出现关键词列表中的任意词"""
    for kw in keywords:
        if kw in text:
            return True
    return False


# ----------------------------------------------------------------
# 主函数：验证命盘
# ----------------------------------------------------------------
def verify_chart(user_id):
    """
    主逻辑：读取用户上传的命盘与人生轨迹资料，
    对比后输出评分、置信度与 life_tags。
    """

    # 假设路径结构（未来可连接 Supabase）
    base_dir = "./data"
    chart_file = os.path.join(base_dir, f"{user_id}_chart.json")
    life_file = os.path.join(base_dir, f"{user_id}_life.json")
    verified_file = os.path.join(base_dir, "verified_birth_profiles.json")

    # ----------------------------------------------------------------
    # 1. 读取命盘与人生轨迹
    # ----------------------------------------------------------------
    if not os.path.exists(chart_file) or not os.path.exists(life_file):
        return {"status": "error", "msg": "缺少命盘或人生资料文件"}

    with open(chart_file, "r", encoding="utf-8") as f:
        chart_data = json.load(f)

    with open(life_file, "r", encoding="utf-8") as f:
        life_data = json.load(f)

    # ----------------------------------------------------------------
    # 2. 比对关键事件（示例逻辑）
    # ----------------------------------------------------------------
    matched = []
    unmatched = []
    total_weight = 0
    gained_score = 0

    for ev in life_data.get("events", []):
        key = ev.get("key", "")
        desc = ev.get("desc", "")
        weight = ev.get("weight", 1.0)
        total_weight += weight

        # 简单匹配逻辑：若命盘描述文本中含有关键字
        if fuzzy_match(str(chart_data), [key, desc]):
            matched.append(ev)
            gained_score += weight
        else:
            # 模糊相似度判定
            score = similarity(str(chart_data), desc)
            if score > 0.45:
                matched.append(ev)
                gained_score += weight * score
            else:
                unmatched.append(ev)

    # ----------------------------------------------------------------
    # 3. 计算综合评分
    # ----------------------------------------------------------------
    score = round(gained_score / total_weight, 3) if total_weight else 0.0
    confidence = "高" if score >= 0.85 else "中" if score >= 0.65 else "低"

    # ----------------------------------------------------------------
    # 4. life_tags 提取（用于同命匹配）
    # ----------------------------------------------------------------
    life_tags = {
        "career_type": life_data.get("career_type", ""),
        "marriage_status": life_data.get("marriage_status", ""),
        "children": life_data.get("children", 0),
        "study_abroad": any("留学" in ev.get("desc", "") for ev in life_data.get("events", [])),
        "major_accident": next((ev.get("desc") for ev in life_data.get("events", []) if "病" in ev.get("desc", "") or "伤" in ev.get("desc", "")), None)
    }

    # ----------------------------------------------------------------
    # 5. 生成验证结果
    # ----------------------------------------------------------------
    result = {
        "user_id": user_id,
        "verified_chart_id": chart_data.get("chart_id", "unknown"),
        "score": score,
        "confidence": confidence,
        "matched_events": matched,
        "unmatched_events": unmatched,
        "life_tags": life_tags,
        "status": "verified" if score >= 0.75 else "unverified",
        "verified_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # ----------------------------------------------------------------
    # 6. 写入或更新验证档案
    # ----------------------------------------------------------------
    os.makedirs(base_dir, exist_ok=True)
    if os.path.exists(verified_file):
        with open(verified_file, "r", encoding="utf-8") as vf:
            try:
                verified_data = json.load(vf)
            except:
                verified_data = []
    else:
        verified_data = []

    # 更新或新增
    existing = next((r for r in verified_data if r["user_id"] == user_id), None)
    if existing:
        existing.update(result)
    else:
        verified_data.append(result)

    with open(verified_file, "w", encoding="utf-8") as vf:
        json.dump(verified_data, vf, ensure_ascii=False, indent=2)

    return result


# ----------------------------------------------------------------
# 手动测试入口
# ----------------------------------------------------------------
if __name__ == "__main__":
    # 模拟数据
    os.makedirs("./data", exist_ok=True)

    chart_demo = {
        "chart_id": "c_demo",
        "source": "wenmo",
        "birth_datetime": "1975-05-10 23:10",
        "main_star": "天府",
        "notes": "命宫在巳，武曲、天同格局"
    }

    life_demo = {
        "career_type": "设计行业",
        "marriage_status": "晚婚",
        "children": 1,
        "events": [
            {"key": "母亲早逝", "desc": "2003年母亲去世", "weight": 2.0},
            {"key": "留学", "desc": "2006年海外留学", "weight": 1.0},
            {"key": "事业", "desc": "2010年获设计奖项", "weight": 1.5},
            {"key": "婚姻", "desc": "晚婚，妻子比自己大", "weight": 1.2}
        ]
    }

    with open("./data/u_demo_chart.json", "w", encoding="utf-8") as f:
        json.dump(chart_demo, f, ensure_ascii=False, indent=2)

    with open("./data/u_demo_life.json", "w", encoding="utf-8") as f:
        json.dump(life_demo, f, ensure_ascii=False, indent=2)

    result = verify_chart("u_demo")
    print(json.dumps(result, ensure_ascii=False, indent=2))
