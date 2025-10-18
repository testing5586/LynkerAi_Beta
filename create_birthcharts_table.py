import os
from supabase import create_client, Client

# Initialize the Supabase client
url: str = os.getenv('SUPABASE_URL')
key: str = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(url, key)

# Function to create the birthcharts table
def create_birthcharts_table():
    birthcharts_table = supabase.table('birthcharts').create(
        {
            'id': {'type': 'integer', 'autoIncrement': True, 'primaryKey': True},
            'name': {'type': 'text', 'notNull': True},
            'gender': {'type': 'text', 'notNull': True},
            'birth_time': {'type': 'timestamp', 'notNull': True},
            'ziwei_palace': {'type': 'text'},
            'main_star': {'type': 'text'},
            'shen_palace': {'type': 'text'}
        }
    )
    return birthcharts_table

# Call the function to create the table
create_birthcharts_table()