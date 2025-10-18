import os
from supabase import create_client, Client
from match_palace import calculate_match_score

# Supabase URL and Key (Ensure these are securely managed in your environment)
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def create_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_user_birthchart_data(client: Client, user_id: int):
    response = client.from_('birthcharts').select('ziwei_palace, main_star, shen_palace').eq('id', user_id).execute()
    if response.data:
        return response.data[0]
    else:
        raise ValueError(f"No data found for user_id: {user_id}")

def main():
    client = create_supabase_client()
    
    # Fetch birthchart data for users with id 2 and 3
    user2_data = fetch_user_birthchart_data(client, 2)
    user3_data = fetch_user_birthchart_data(client, 3)

    # Extract the relevant fields
    user2_palace_data = {
        'ziwei_palace': user2_data['ziwei_palace'],
        'main_star': user2_data['main_star'],
        'shen_palace': user2_data['shen_palace']
    }

    user3_palace_data = {
        'ziwei_palace': user3_data['ziwei_palace'],
        'main_star': user3_data['main_star'],
        'shen_palace': user3_data['shen_palace']
    }

    # Calculate and print match score
    match_score = calculate_match_score(user2_palace_data, user3_palace_data)
    print(f"The match score between user 2 and user 3 is: {match_score}")

if __name__ == "__main__":
    main()