import random

AI_ROLES = {
    "master": "Master AI 🧠",
    "leader": "Group Leader 🧩",
    "child": "Child AI 🤖"
}

def process_message(message):
    """处理用户消息并生成AI回复"""
    replies = [
        f"{AI_ROLES['master']}: 我已分析此主题，准备总结核心结论。",
        f"{AI_ROLES['leader']}: 我将协调下属 AI 执行指令。",
        f"{AI_ROLES['child']}: 正在执行命盘匹配与规律分析任务..."
    ]
    random.shuffle(replies)
    return replies
