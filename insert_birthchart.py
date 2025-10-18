import os
import asyncio
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def insert_birthchart():
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