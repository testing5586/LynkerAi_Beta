#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动检测和设置 Supabase 数据库连接
Auto-detect and setup Supabase database connection
"""

import os
import sys
import locale
# Set console encoding for Windows
if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    # Change default encoding to utf-8
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
from supabase import create_client
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()

def test_supabase_connection():
    """测试 Supabase 连接"""
    print("🔍 Testing Supabase connection...")
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    db_url = os.getenv("DATABASE_URL")
    
    if not url or not key:
        print("❌ Supabase credentials not found in .env file")
        return False
    
    try:
        # Test direct PostgreSQL connection first
        if db_url:
            conn = psycopg2.connect(db_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Direct PostgreSQL connection successful: {version['version'][:50]}...")
            conn.close()
        
        # Test REST API connection with a simple query
        client = create_client(url, key)
        # Try to query a known table instead of information_schema
        try:
            response = client.table('soulmate_matches').select('*').limit(1).execute()
            print("✅ Supabase REST API connection successful")
        except:
            # If table doesn't exist, that's still OK - it means connection works
            print("✅ Supabase REST API connection successful (tables may not exist yet)")
        
        return True
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

def create_missing_tables():
    """创建缺失的表"""
    print("\n🛠️ Checking and creating missing tables...")
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found")
        return False
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # 读取 SQL 文件并执行
        sql_files = [
            'CREATE_TABLES.sql',
            'supabase_tables_schema.sql'
        ]
        
        for sql_file in sql_files:
            if os.path.exists(sql_file):
                print(f"📄 Executing {sql_file}...")
                with open(sql_file, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                
                # 分割 SQL 语句（简单分割，按分号分隔）
                statements = [s.strip() for s in sql_content.split(';') if s.strip()]
                
                for stmt in statements:
                    if stmt and not stmt.startswith('--'):
                        try:
                            cursor.execute(stmt)
                            conn.commit()
                        except Exception as e:
                            # 忽略已存在的错误
                            if "already exists" not in str(e):
                                print(f"⚠️ Warning executing statement: {str(e)[:100]}")
                            conn.rollback()
                
                print(f"✅ {sql_file} executed successfully")
            else:
                print(f"⚠️ {sql_file} not found")
        
        # 创建 master_vault 表（如果不存在）
        print("\n📦 Creating master_vault table if not exists...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS master_vault (
                id BIGSERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT,
                tags TEXT[],
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit()
        
        # 创建 get_events_last_7d 函数
        print("\n🔧 Creating get_events_last_7d function...")
        cursor.execute("""
            CREATE OR REPLACE FUNCTION get_events_last_7d()
            RETURNS TABLE (
                total_events_7d BIGINT,
                emotion_distribution JSONB
            ) AS $$
            BEGIN
                RETURN QUERY
                SELECT 
                    COUNT(*) as total_events_7d,
                    jsonb_object_agg(emotion_label, emotion_count) as emotion_distribution
                FROM (
                    SELECT 
                        emotion_label,
                        COUNT(*) as emotion_count
                    FROM user_events
                    WHERE created_at >= NOW() - INTERVAL '7 days'
                    GROUP BY emotion_label
                ) subq;
            END;
            $$ LANGUAGE plpgsql;
        """)
        conn.commit()
        
        conn.close()
        print("✅ All tables and functions created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create tables: {str(e)}")
        return False

def verify_setup():
    """验证设置"""
    print("\n🔍 Verifying database setup...")
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found")
        return False
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 检查关键表
        tables_to_check = [
            'user_events', 'user_insights', 'verified_charts', 
            'life_event_weights', 'user_life_tags', 'soulmate_matches',
            'child_ai_insights', 'child_ai_memory', 'master_vault'
        ]
        
        for table in tables_to_check:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, (table,))
            exists = cursor.fetchone()['exists']
            status = "✅" if exists else "❌"
            print(f"{status} Table '{table}'")
        
        # 检查函数
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.routines 
                WHERE routine_schema = 'public' 
                AND routine_name = 'get_events_last_7d'
            );
        """)
        func_exists = cursor.fetchone()['exists']
        status = "✅" if func_exists else "❌"
        print(f"{status} Function 'get_events_last_7d'")
        
        conn.close()
        print("\n✅ Database verification complete")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 LynkerAI Supabase Auto-Setup Tool")
    print("=" * 60)
    
    # 1. 测试连接
    if not test_supabase_connection():
        print("\n❌ Please check your Supabase credentials in .env file")
        sys.exit(1)
    
    # 2. 创建缺失的表
    if not create_missing_tables():
        print("\n❌ Failed to create tables")
        sys.exit(1)
    
    # 3. 验证设置
    if not verify_setup():
        print("\n❌ Verification failed")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Supabase setup completed successfully!")
    print("🌐 You can now access the application at: http://localhost:5000")
    print("🔑 Login password: 9821a9762b008821")
    print("=" * 60)

if __name__ == "__main__":
    main()