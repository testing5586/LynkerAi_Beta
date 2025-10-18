import os
from supabase import create_client, Client
import pandas as pd

# 如果需要安装Python依赖，使用该行格式（不要用pip install，系统会自动处理）
# 依赖：supabase pandas

def initialize_supabase() -> Client:
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

def fetch_match_results(supabase: Client) -> pd.DataFrame:
    response = supabase.table("match_results").select("*").execute()
    data = response.data
    return pd.DataFrame(data)

def calculate_average_score(df: pd.DataFrame) -> float:
    return df['match_score'].mean()

def score_distribution(df: pd.DataFrame, bins: list) -> pd.Series:
    return pd.cut(df['match_score'], bins=bins).value_counts().sort_index()

def top_matches(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    sorted_df = df.sort_values(by='match_score', ascending=False).head(top_n)
    return sorted_df[['user_a_name', 'user_b_name', 'match_score', 'matching_fields']]

def main():
    supabase = initialize_supabase()
    match_results = fetch_match_results(supabase)

    # Calculate average match score
    average_score = calculate_average_score(match_results)
    print(f"Average Match Score: {average_score:.2f}")

    # Calculate score distribution
    bins = [0, 20, 40, 60, 80, 100]  # Example bins for score distribution
    distribution = score_distribution(match_results, bins)
    print("Score Distribution:")
    for r in distribution.index:
        print(f"Scores {r}: {distribution[r]} matches")

    # Display top 10 matches
    top_10 = top_matches(match_results)
    print("\nTop 10 Matches:")
    print(top_10.to_string(index=False))

if __name__ == "__main__":
    main()