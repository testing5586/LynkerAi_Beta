#!/usr/bin/env python3
"""
==========================================================
Supabase users 表结构自动修复脚本
==========================================================
功能：
1. 检测 public.users 表的字段是否完整
2. 自动添加缺失的 Google Drive 相关字段
3. 刷新 PostgREST 缓存
"""

from supabase_init import init_supabase


def check_users_table_schema():
    """
    检查 users 表是否包含必需的 Google Drive 字段
    
    返回:
        缺失字段列表
    """
    supabase = init_supabase()
    
    if supabase is None:
        print("❌ Supabase 未连接，无法检查表结构")
        return None
    
    # 必需的字段
    required_fields = {
        "drive_connected": "BOOLEAN",
        "drive_access_token": "TEXT",
        "drive_email": "TEXT"
    }
    
    try:
        # 尝试查询一条数据以检测字段
        print("🔍 正在检测 Supabase users 表...")
        result = supabase.table("users").select("*").limit(1).execute()
        print("✅ 已找到表：users")
        
        # 检查现有字段
        existing_fields = set()
        if result.data and len(result.data) > 0:
            existing_fields = set(result.data[0].keys())
        else:
            # 如果表为空，尝试插入测试数据来检测字段
            try:
                test_result = supabase.table("users").select("drive_connected, drive_access_token, drive_email").limit(1).execute()
                existing_fields.update(["drive_connected", "drive_access_token", "drive_email"])
            except:
                pass
        
        # 检测缺失字段
        missing_fields = []
        for field_name in required_fields.keys():
            if field_name not in existing_fields:
                missing_fields.append(field_name)
        
        return missing_fields
        
    except Exception as e:
        error_msg = str(e)
        
        # 如果错误信息包含字段不存在的提示，说明字段缺失
        if "column" in error_msg.lower() or "does not exist" in error_msg.lower():
            print(f"⚠️ 检测到字段缺失：{error_msg}")
            return list(required_fields.keys())
        else:
            print(f"❌ 检查表结构失败：{e}")
            return None


def fix_users_table_schema(missing_fields):
    """
    修复 users 表结构，添加缺失的字段
    
    参数:
        missing_fields: 缺失字段列表
    
    返回:
        修复结果
    """
    if not missing_fields:
        print("✅ 表结构完整，无需修复")
        return {"success": True, "message": "No fix needed"}
    
    supabase = init_supabase()
    
    if supabase is None:
        print("❌ Supabase 未连接，无法修复")
        return {"success": False, "error": "Supabase not connected"}
    
    print(f"⚙️ 修复中：添加缺失字段 {', '.join(missing_fields)}")
    
    # 构建 SQL 语句
    sql_statements = []
    
    # 添加字段
    for field in missing_fields:
        if field == "drive_connected":
            sql_statements.append("ADD COLUMN IF NOT EXISTS drive_connected BOOLEAN DEFAULT FALSE")
        elif field == "drive_access_token":
            sql_statements.append("ADD COLUMN IF NOT EXISTS drive_access_token TEXT")
        elif field == "drive_email":
            sql_statements.append("ADD COLUMN IF NOT EXISTS drive_email TEXT")
    
    # 完整的 ALTER TABLE 语句
    alter_sql = f"ALTER TABLE public.users {', '.join(sql_statements)};"
    
    try:
        # 执行 SQL（使用 Supabase 的 RPC 或直接连接）
        # 注意：Supabase Python SDK 不直接支持 DDL，需要使用 PostgREST 的 rpc 功能
        # 或者使用 psycopg2 直接连接数据库
        
        # 方案1：使用 psycopg2（需要 DATABASE_URL）
        import os
        database_url = os.getenv("DATABASE_URL")
        
        if database_url:
            import psycopg2
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            
            # 执行 ALTER TABLE
            cursor.execute(alter_sql)
            
            # 刷新 PostgREST 缓存
            cursor.execute("NOTIFY pgrst, 'reload schema';")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print("✅ 修复完成并刷新缓存！")
            return {"success": True, "message": "Schema fixed successfully"}
        else:
            print("⚠️ 无法获取 DATABASE_URL，请在 Supabase Dashboard 手动执行以下 SQL：")
            print(f"\n{alter_sql}\nNOTIFY pgrst, 'reload schema';\n")
            return {"success": False, "error": "DATABASE_URL not found", "sql": alter_sql}
            
    except Exception as e:
        print(f"❌ 修复失败：{e}")
        print(f"请手动执行以下 SQL：\n{alter_sql}\n")
        return {"success": False, "error": str(e), "sql": alter_sql}


def auto_fix_schema():
    """
    自动检测并修复 users 表结构
    """
    print("=" * 60)
    print("Supabase users 表结构自动修复工具")
    print("=" * 60)
    print()
    
    # 1. 检查表结构
    missing_fields = check_users_table_schema()
    
    if missing_fields is None:
        print("❌ 无法检查表结构，请检查 Supabase 连接")
        return False
    
    if not missing_fields:
        print("✅ 表结构完整，所有字段都已存在！")
        return True
    
    print(f"⚠️ 发现缺失字段：{', '.join(missing_fields)}")
    print()
    
    # 2. 修复表结构
    result = fix_users_table_schema(missing_fields)
    
    if result["success"]:
        print("\n🎉 表结构修复完成！")
        return True
    else:
        print("\n⚠️ 自动修复失败，请手动执行 SQL")
        if "sql" in result:
            print(f"\nSQL 语句：\n{result['sql']}\n")
        return False


# ============================================================
# 主程序入口
# ============================================================
if __name__ == "__main__":
    try:
        # 先检查是否安装了 psycopg2
        try:
            import psycopg2
            print("✅ psycopg2 已安装\n")
        except ImportError:
            print("⚠️ psycopg2 未安装，将只能显示 SQL 语句")
            print("💡 提示：运行 'uv add psycopg2-binary' 安装依赖\n")
        
        # 执行自动修复
        auto_fix_schema()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 发生错误：{e}")
