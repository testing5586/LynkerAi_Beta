import os

# 获取项目根目录（向上两级）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROMPT_DIR = os.path.join(BASE_DIR, "LKK-Knowledge-Core", "prompts")

def load_latest_wizard():
    """
    动态加载最新版本的问卷
    从 LKK-Knowledge-Core/prompts/ 目录中查找 true_birth_wizard_vX.txt
    """
    if not os.path.exists(PROMPT_DIR):
        raise FileNotFoundError(f"❌ 问卷目录不存在: {PROMPT_DIR}")
    
    files = [f for f in os.listdir(PROMPT_DIR) if f.startswith("true_birth_wizard_")]
    if not files:
        raise FileNotFoundError("❌ 没有找到任何 true_birth_wizard_xxx.txt 模板")

    # 版本号排序，v10 > v9 > v1
    latest = sorted(files, key=lambda x: int(x.split("_v")[1].split(".")[0]), reverse=True)[0]
    
    with open(os.path.join(PROMPT_DIR, latest), "r", encoding="utf-8") as f:
        content = f.read()
    
    print(f"✅ 已加载问卷: {latest}")
    return content
