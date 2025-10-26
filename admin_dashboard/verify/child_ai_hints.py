# admin_dashboard/verify/child_ai_hints.py

from openai import OpenAI

client = OpenAI()

def generate_child_ai_hint(bazi_chart, ziwei_chart, conversation_memory):
    """
    child ai 内部推理：根据用户回答 → 识别可能的关键事件 → 提出“提示性验证方向”
    返回格式为 machine_hint，不直接对用户说。
    """

    prompt = f"""
你是一个隐形的批命辅助分析 AI，不直接与用户对话。

你会收到：
1) 八字命盘结构
2) 紫微斗数命盘结构
3) 用户至今聊到的人生事件信息

你的任务：
- 从命理结构中找出「最有可能应验的事件模式」
- 结合用户已提到的人生细节
- 提供 **1 条可能值得「灵伴」继续深入询问的方向**

你的输出必须是 JSON，只允许如下结构：

{{
  "should_ask": true/false,
  "suggested_question": "（给灵伴使用、温柔、委婉）"
}}

示例输出：
{{
  "should_ask": true,
  "suggested_question": "我听到你提到童年情感体验可能比较敏感，你愿意说说你当时和母亲相处最深刻的一件小事吗？"
}}

现在请基于以下信息生成提示：

八字命盘结构：
{bazi_chart}

紫微斗数命盘结构：
{ziwei_chart}

用户人生回忆对话内容：
{conversation_memory}

输出：
    """

    # 如果没有命盘数据，直接返回不提问
    if not bazi_chart and not ziwei_chart:
        return '{"should_ask": false}'
    
    r = client.chat.completions.create(
        model="gpt-4o-mini",  # 使用 gpt-4o-mini 而不是 gpt-4.1
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    try:
        content = r.choices[0].message.content
        if content:
            return content.strip()
        return '{"should_ask": false}'
    except Exception as e:
        print(f"⚠️ Child AI hint 生成异常: {e}")
        return '{"should_ask": false}'
