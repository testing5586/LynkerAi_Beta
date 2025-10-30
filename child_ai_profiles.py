# -*- coding: utf-8 -*-
"""
child_ai_profiles.py
用于管理每个用户子AI的个性与语气设定
"""

# -*- coding: utf-8 -*-
import sys, io
# Only wrap stdout/stderr if not already wrapped
if not hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if not hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from datetime import datetime

# ========================
# 人格模板定义
# ========================
AI_PERSONALITY_TEMPLATES = {
    "理性分析型": {
        "tone": "理性",
        "empathy_level": 2,
        "logic_level": 5,
        "creativity_level": 3,
        "description": "以事实和逻辑为主，偏好分析命盘结构与趋势。"
    },
    "感性安慰型": {
        "tone": "温柔",
        "empathy_level": 5,
        "logic_level": 2,
        "creativity_level": 4,
        "description": "重视情感连结与安慰，用心倾听命主的故事。"
    },
    "灵修导师型": {
        "tone": "平静",
        "empathy_level": 4,
        "logic_level": 3,
        "creativity_level": 5,
        "description": "以精神成长与命理悟性为导向，洞察深层因缘。"
    },
    "幽默轻松型": {
        "tone": "幽默",
        "empathy_level": 3,
        "logic_level": 3,
        "creativity_level": 5,
        "description": "用轻松的方式解释命理，善于化解紧张氛围。"
    }
}


# ========================
# 读取或创建子AI人格
# ========================
def get_or_create_child_ai_profile(supabase_client, user_id, personality="感性安慰型"):
    """读取或创建子AI人格资料"""
    try:
        result = supabase_client.table("child_ai_profiles").select("*").eq("user_id", user_id).execute()
        if result.data:
            profile = result.data[0]
            print(f"[读取] 读取AI人格：{profile['personality_name']} ({user_id})")
            return profile
        else:
            tpl = AI_PERSONALITY_TEMPLATES.get(personality, AI_PERSONALITY_TEMPLATES["感性安慰型"])
            record = {
                "user_id": user_id,
                "personality_name": personality,
                **tpl,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            supabase_client.table("child_ai_profiles").insert(record).execute()
            print(f"[创建] 已为 {user_id} 创建新AI人格：{personality}")
            return record
    except Exception as err:
        print(f"[错误] 读取/创建 AI 人格失败：{err}")
        return None

# ========================
# 用于生成语气化的回应
# ========================
def apply_personality_tone(profile, insight_text):
    """根据子AI人格调整报告语气"""
    if not profile:
        return insight_text

    tone = profile.get("tone", "理性")
    empathy = profile.get("empathy_level", 3)
    desc = profile.get("description", "")

    if tone == "温柔":
        return f"[温柔] {insight_text}\n[提示] 你的AI很温柔地提醒：{desc}"
    elif tone == "平静":
        return f"[平静] {insight_text}\n[启示] 平静启示：{desc}"
    elif tone == "幽默":
        return f"[幽默] {insight_text}\n[轻松] 轻松一句：{desc}"
    else:
        return f"[理性] {insight_text}\n[分析] 理性分析：{desc}"

# ========================
# 独立测试命令
# ========================
if __name__ == "__main__":
    from supabase_init import get_supabase
    supabase = get_supabase()

    user_id = "u_demo"
    profile = get_or_create_child_ai_profile(supabase, user_id, "灵修导师型")

    test_insight = "你与 u_test 的命理相似度为 0.911，共同特征：设计行业、晚婚。"
    print(apply_personality_tone(profile, test_insight))

def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        msg = " ".join(str(a) for a in args)
        print(msg.encode('utf-8', 'replace').decode('utf-8'))
