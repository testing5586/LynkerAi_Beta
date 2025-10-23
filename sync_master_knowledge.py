import os
from supabase import create_client
from docx import Document
from datetime import datetime

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

LOCAL_PATH = "docs/lynker_ai_core_index_v2.docx"
VERSION = "v2"

def read_local_doc():
    doc = Document(LOCAL_PATH)
    content = "\n".join([p.text for p in doc.paragraphs])
    return content.strip()

def get_cloud_version():
    data = supabase.table("knowledge_base").select("*").eq("version", VERSION).execute()
    return data.data[0] if data.data else None

def sync_to_supabase():
    local_content = read_local_doc()
    cloud_data = get_cloud_version()

    if cloud_data:
        # 对比内容长度判断是否需要更新
        if len(local_content) != len(cloud_data["content"]):
            supabase.table("knowledge_base").update({
                "content": local_content,
                "updated_at": datetime.now().isoformat()
            }).eq("version", VERSION).execute()
            print("☁️ Supabase 已更新最新版本。")
        else:
            print("✅ 云端与本地一致，无需更新。")
    else:
        supabase.table("knowledge_base").insert({
            "title": "灵客AI核心思想索引表 v2",
            "content": local_content,
            "version": VERSION
        }).execute()
        print("🌱 已上传新的知识库版本。")

if __name__ == "__main__":
    sync_to_supabase()
