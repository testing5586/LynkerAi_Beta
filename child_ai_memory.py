"""
child_ai_memory.py
------------------------------------
📘 功能：
Lynker 子AI记忆仓库系统

从 child_ai_insights 提取信息，
自动生成记忆摘要，
保存至 Supabase 或本地 JSON，
并预留 Google Drive 同步接口。
------------------------------------
运行方式：
python child_ai_memory.py
"""

import json, os
from datetime import datetime

try:
    from supabase_init import get_supabase
    supabase = get_supabase()
except Exception as e:
    supabase = None
    print(f"⚠️ Supabase连接失败，转为本地模式: {e}")


# ✅ 本地备份函数
def save_local_backup(filename, data):
    os.makedirs("./data", exist_ok=True)
    with open(f"./data/{filename}", "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")
    print(f"💾 本地备份 → {filename}")


# ✅ 预留 Google Drive 接口
def save_to_google_drive(user_id, memory_record):
    """
    📂 未来功能：用户授权后写入 Google Drive
    Scope: https://www.googleapis.com/auth/drive.file
    Path: My Drive / LynkerAI / memory / u_{user_id}_memory.json
    """
    # TODO: Integrate OAuth 2.0 + Drive API
    print(f"☁️ [预留] 将写入 Google Drive：{user_id} - {memory_record['summary']}")


# ✅ 从 child_ai_insights 提取用户的匹配记忆
def extract_ai_memories(user_id):
    if not supabase:
        print("⚠️ 无法连接 Supabase，使用本地模式。")
        return []

    resp = supabase.table("child_ai_insights").select("*").eq("user_id", user_id).execute()
    data = resp.data if resp and resp.data else []
    if not data:
        print("⚠️ 没有找到任何洞察记录。")
        return []

    memories = []
    for record in data:
        partner = record.get("partner_id", "未知")
        # 🧩 自动展开 shared_tags 的各种类型结构
        tags = record.get("shared_tags", [])

        # 若是字符串 → 尝试反序列化
        if isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except:
                tags = [tags]

        # 若是 dict → 取值
        if isinstance(tags, dict):
            tags = list(tags.values())

        # 若是嵌套 list → 展平
        if isinstance(tags, list):
            flat_tags = []
            for t in tags:
                if isinstance(t, list):
                    flat_tags.extend(t)
                elif isinstance(t, dict):
                    flat_tags.extend(list(t.values()))
                else:
                    flat_tags.append(str(t))
            tags = flat_tags

        # 统一转字符串
        tags_str = "、".join([str(t) for t in tags if t])
        sim = round(record.get("similarity", 0.0), 3)
        summary = f"与 {partner} 共鸣 ({sim})：{tags_str}"
        memories.append({
            "user_id": user_id,
            "partner_id": partner,
            "tags": tags,
            "summary": summary,
            "created_at": datetime.now().isoformat()
        })
    print(f"🧠 已提取 {len(memories)} 条AI记忆。")
    return memories


# ✅ 保存至 Supabase
def save_ai_memories(user_id, memories):
    if not memories:
        print("⚠️ 没有可保存的记忆。")
        return

    for mem in memories:
        try:
            if supabase:
                supabase.table("child_ai_memory").insert(mem).execute()
                print(f"💾 已保存至 Supabase.child_ai_memory → {mem['partner_id']}")
            else:
                save_local_backup("child_ai_memory_backup.jsonl", mem)
            # ☁️ 可选未来同步
            # save_to_google_drive(user_id, mem)
        except Exception as e:
            print(f"⚠️ Supabase写入失败，保存本地：{e}")
            save_local_backup("child_ai_memory_backup.jsonl", mem)


# ✅ 主执行函数
def run_child_ai_memory(user_id="u_demo"):
    print(f"📜 子AI记忆生成中：{user_id}")
    memories = extract_ai_memories(user_id)
    save_ai_memories(user_id, memories)
    print("✅ 子AI记忆同步完成。")


# ✅ 测试运行
if __name__ == "__main__":
    run_child_ai_memory("u_demo")
