import os
from supabase import create_client, Client
from match_palace import calculate_match_score

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def fetch_birthcharts():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table("birthcharts").select("*").execute()
    return response.data

def get_matching_scores(current_user_id, birthcharts):
    current_user_chart = None
    for chart in birthcharts:
        if chart['id'] == current_user_id:
            current_user_chart = chart
            break
    
    if not current_user_chart:
        raise ValueError(f"User with id {current_user_id} not found in birthcharts.")

    scores = []
    for chart in birthcharts:
        if chart['id'] != current_user_id:
            score, common_items = calculate_match_score(current_user_chart, chart)
            scores.append({
                'name': chart['name'],
                'score': score,
                'common_items': common_items
            })

    scores.sort(key=lambda x: x['score'], reverse=True)
    return scores[:5]

def main():
    try:
        birthcharts = fetch_birthcharts()
        top_matches = get_matching_scores(2, birthcharts)
        
        print("Top 5 Matches:")
        for match in top_matches:
            print(f"Name: {match['name']}, Score: {match['score']}, Common Items: {match['common_items']}")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()