import asyncio
from supabase import create_client, Client

SUPABASE_URL = "https://tojtfjkreudspzhkwdwj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvanRmamtyZXVkc3B6aGt3ZHdqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkwMjc3OTksImV4cCI6MjA3NDYwMzc5OX0.7KTJ9yqjGzXA2wmIMUMiAVXBhqQGLu_JRMabcRQrfaU"

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