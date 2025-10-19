import os
import asyncio
from supabase import create_client, Client
from ai_guard_middleware import check_permission

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def insert_birthchart(user_id=1):
    # LynkerAI 防火墙检查
    resp = check_permission(user_id)
    if resp["status"] != "ok":
        print(resp)
        return resp

    # Initialize Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Define the birthchart data
    birthchart_data = {
        "name": "命主C",
        "gender": "女",
        "birth_time": "1990-05-20T15:30:00",
        "ziwei_palace": "巳",
        "main_star": "廉贞",
        "shen_palace": "卯"
    }
    
    # Insert the data into the birthcharts table
    response = supabase.table("birthcharts").insert(birthchart_data).execute()
    
    # Print the response
    print(response)

if __name__ == "__main__":
    insert_birthchart()