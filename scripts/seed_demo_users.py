import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from supabase_init import init_supabase
from datetime import datetime

def upsert_user(supabase, user_id, career, marriage, children, study_abroad, major_accident):
    supabase.table("user_life_tags").upsert({
        "user_id": user_id,
        "career_type": career,
        "marriage_status": marriage,
        "children": children,
        "study_abroad": study_abroad,
        "major_accident": major_accident,
        "event_count": 4,
        "updated_at": datetime.now().isoformat()
    }).execute()
    print(f"✅ upsert user_life_tags → {user_id}")

if __name__ == "__main__":
    sb = init_supabase()
    upsert_user(sb, "u_test1", "设计行业", "晚婚", 1, True, None)
    upsert_user(sb, "u_test2", "科技行业", "已婚", 2, False, "2015年手术")
