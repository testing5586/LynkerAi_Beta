from supabase import create_client, Client
import os

# 从环境变量读取 Supabase 配置
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_birthchart_data():
    data = [
        {
            "name": "命主A",
            "gender": "男",
            "birth_time": "1975-05-10T23:10:00",
            "ziwei_palace": "巳",
            "main_star": "天府",
            "shen_palace": "巳"
        },
        {
            "name": "命主B",
            "gender": "女",
            "birth_time": "1982-08-14T09:15:00",
            "ziwei_palace": "午",
            "main_star": "武曲",
            "shen_palace": "巳"
        }
    ]
    response = supabase.table("birthcharts").insert(data).execute()
    print("✅ 插入结果:", response.data)

if __name__ == "__main__":
    insert_birthchart_data()
