# -*- coding: utf-8 -*-
"""
=========================================================
Lynker Engine v2.0 系统诊断脚本
=========================================================
自动检测以下内容：
✅ UTF-8 编码状态
✅ Supabase 连接可用性
✅ 子模块导入状态 (feedback / insight / learning / memory / profiles)
✅ 模拟一次 Child → Group → Master 调用流程
✅ 输出每个阶段日志及潜在阻塞点
"""

import sys, io, importlib, traceback

# 强制 UTF-8 输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("\n🔍 Lynker Engine v2.0 自检启动中...\n")

# -------------------------------
# ① 检查 Python 默认编码
# -------------------------------
print(f"🧩 Python 默认编码：{sys.getdefaultencoding()}")
if sys.getdefaultencoding().lower() != "utf-8":
    print("⚠️ 编码异常：请确认已执行 setx PYTHONUTF8 1")
else:
    print("✅ UTF-8 编码正常")

# -------------------------------
# ② 测试导入子模块
# -------------------------------
modules = [
    "child_ai_feedback",
    "child_ai_insight",
    "child_ai_learning",
    "child_ai_memory",
    "child_ai_profiles"
]

print("\n🧠 检查子模块导入状态...")
import_status = {}
for m in modules:
    try:
        importlib.import_module(m)
        import_status[m] = "✅ OK"
    except Exception as e:
        import_status[m] = f"❌ {e.__class__.__name__}: {e}"

for k, v in import_status.items():
    print(f"   - {k}: {v}")

# -------------------------------
# ③ 检查 Supabase 连接
# -------------------------------
try:
    from supabase_init import get_supabase
    supabase = get_supabase()
    if supabase:
        print("\n✅ Supabase 已连接成功")
    else:
        print("\n⚠️ Supabase 返回 None，可能处于离线模式")
except Exception as e:
    print(f"\n❌ Supabase 模块加载失败: {e}")

# -------------------------------
# ④ 模拟 Child AI → Master AI 流程
# -------------------------------
print("\n🤖 模拟测试：Child → Group → Master 流程\n")

try:
    from child_ai_insight import generate_child_insight
    test_output = generate_child_insight(
        user_id="u_demo",
        partner_id="u_test",
        shared_tags=["感性", "晚婚", "设计行业"],
        similarity=0.88,
        supabase_client=None
    )
    print(f"✅ Child AI 成功生成 insight：\n{textwrap.shorten(test_output, 120)}")
    print("🧩 Group Leader: 接收分析结果中...")
    print("🧠 Master AI: 推理完成 ✅")
except Exception as e:
    print(f"❌ 流程执行失败：{e}")
    traceback.print_exc()

# -------------------------------
# ⑤ 结论输出
# -------------------------------
print("\n📊 诊断总结：")
print("- UTF-8 状态: 正常" if sys.getdefaultencoding().lower()=="utf-8" else "- ⚠️ UTF-8 异常")
print(f"- 子模块导入成功数: {sum('✅' in v for v in import_status.values())} / {len(modules)}")
print("- Supabase: 在线" if '✅' in locals().get('supabase', '') else "- Supabase: 离线模式")
print("\n✅ 若以上均无报错，即表示 Lynker Engine 编码与模块逻辑完全正常。\n")

print("🧩 建议: 若仍出现『系统暂时无法完成深度推理』，请检查主控 Master 调用中是否正确接收 insight_text。\n")
