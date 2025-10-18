import os
from itertools import combinations
from supabase import create_client, Client
from match_palace import calculate_match_score

# Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def create_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_all_birthcharts(client: Client):
    """从 birthcharts 表获取所有命盘数据"""
    response = client.from_('birthcharts').select('id, name, ziwei_palace, main_star, shen_palace').execute()
    return response.data or []

def save_match_result(client: Client, user_a, user_b, score, fields):
    """将匹配结果写入 match_results 表"""
    result = {
        'user_a_id': user_a['id'],
        'user_a_name': user_a['name'],
        'user_b_id': user_b['id'],
        'user_b_name': user_b['name'],
        'match_score': score,
        'matching_fields': ', '.join(fields)
    }
    client.from_('match_results').insert(result).execute()

def main():
    client = create_supabase_client()
    charts = fetch_all_birthcharts(client)

    if len(charts) < 2:
        print("⚠️ 数据不足，至少需要 2 条命盘才能比对。")
        return

    print(f"📊 开始匹配 {len(charts)} 条命盘...")

    for user_a, user_b in combinations(charts, 2):
        score, fields = calculate_match_score(user_a, user_b)
        print(f"{user_a['name']} vs {user_b['name']} => {score} 分 ({', '.join(fields) if fields else '无相同项'})")
        save_match_result(client, user_a, user_b, score, fields)

    print("✅ 批量匹配完成，结果已写入 match_results 表。")

if __name__ == "__main__":
    main()
