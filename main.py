import os
from openai import OpenAI
from supabase import create_client, Client

def main():
    print("Python environment ready!")
    print("Packages installed: openai, supabase")
    print("\nTo use OpenAI, set your OPENAI_API_KEY environment variable")
    print("To use Supabase, set SUPABASE_URL and SUPABASE_KEY environment variables")
    
    # Example: Check if API keys are configured
    if os.getenv("OPENAI_API_KEY"):
        print("\n✓ OpenAI API key found")
    else:
        print("\n⚠ OpenAI API key not set")
    
    if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"):
        print("✓ Supabase credentials found")
    else:
        print("⚠ Supabase credentials not set")

if __name__ == "__main__":
    main()
