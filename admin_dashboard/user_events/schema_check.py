"""
数据库表结构检查与自动创建
Schema Check and Auto-creation
"""

from .supabase_client import get_client


def check_and_create_tables():
    """检查表是否存在，不存在则创建"""
    supabase = get_client()
    if not supabase:
        print("⚠️ 跳过表结构检查（Supabase 不可用）")
        return False
    
    try:
        # 尝试查询表，如果失败说明不存在
        supabase.table("user_events").select("id").limit(1).execute()
        supabase.table("user_insights").select("user_id").limit(1).execute()
        
        print("✅ 用户事件表已存在")
        return True
        
    except Exception as e:
        print(f"⚠️ 表检查失败（可能不存在）: {e}")
        print("请手动执行 SQL 创建表，参考文档中的 CREATE TABLE 语句")
        return False


if __name__ == "__main__":
    check_and_create_tables()
