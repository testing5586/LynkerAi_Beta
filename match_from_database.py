import os
from supabase import create_client
from match_palace import calculate_match_score

# 设置 Supabase 的URL和API KEY
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# 创建 Supabase 客户端
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_user_chart(user_id):
    """ 从 birthcharts 表中获取用户的命盘 """
    response = supabase.table('birthcharts').select('ziwei_palace, main_star, shen_palace').eq('id', user_id).execute()
    if response.data:
        return response.data[0]
    else:
        raise ValueError(f"User with id {user_id} not found.")

def main():
    # 指定两个用户的ID
    user1_id = 1
    user2_id = 2
    
    # 从数据库中获取命盘数据
    user1_chart = fetch_user_chart(user1_id)
    user2_chart = fetch_user_chart(user2_id)
    
    # 计算匹配分数
    match_score = calculate_match_score(
        user1_chart['ziwei_palace'],
        user1_chart['main_star'],
        user1_chart['shen_palace'],
        user2_chart['ziwei_palace'],
        user2_chart['main_star'],
        user2_chart['shen_palace'],
    )
    
    # 打印匹配报告
    print(f"Match report between User {user1_id} and User {user2_id}:")
    print(f"Ziwei Palace: {user1_chart['ziwei_palace']} vs {user2_chart['ziwei_palace']}")
    print(f"Main Star: {user1_chart['main_star']} vs {user2_chart['main_star']}")
    print(f"Shen Palace: {user1_chart['shen_palace']} vs {user2_chart['shen_palace']}")
    print(f"Match Score: {match_score}")

if __name__ == "__main__":
    main()