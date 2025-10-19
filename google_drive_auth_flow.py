#!/usr/bin/env python3
"""
==========================================================
Google Drive 绑定流程模拟器
==========================================================
功能：
1. 模拟用户绑定 Google Drive（不调用真实 Google API）
2. 将绑定状态存入 Supabase public.users 表
3. 生成模拟的 access_token
4. 为后续样板账号测试做准备

⚠️ 注意：现在使用 public.users 表（而非 user_profiles）
字段映射：user_id → name, email → email, drive_email → drive_email
"""

from datetime import datetime
from supabase_init import init_supabase


def simulate_drive_auth(user_id: str, email: str):
    """
    模拟 Google Drive 绑定
    
    参数:
        user_id: 用户ID
        email: 用户邮箱（Gmail）
    
    返回:
        绑定结果字典
    """
    supabase = init_supabase()
    
    if supabase is None:
        print("❌ Supabase 未连接，无法绑定")
        return {"success": False, "error": "Supabase not connected"}
    
    # 生成模拟的 access_token
    timestamp = int(datetime.now().timestamp())
    fake_token = f"FAKE_TOKEN_{user_id}_{timestamp}"
    
    # 准备数据（使用 public.users 表）
    data = {
        "name": user_id,  # users 表使用 name 字段作为用户标识
        "email": email,
        "drive_connected": True,
        "drive_access_token": fake_token,
        "drive_email": email  # 专门存储 Google Drive 邮箱
    }
    
    try:
        # 使用 upsert 插入或更新（基于 name 字段）
        result = supabase.table("users").upsert(data).execute()
        
        print(f"✅ 模拟绑定成功：{user_id} ({email})")
        print(f"🔑 Access Token: {fake_token}")
        
        return {
            "success": True,
            "user_id": user_id,
            "email": email,
            "token": fake_token
        }
        
    except Exception as e:
        print(f"❌ 绑定失败：{e}")
        return {"success": False, "error": str(e)}


def check_drive_status(user_id: str):
    """
    检查用户的 Google Drive 绑定状态
    
    参数:
        user_id: 用户ID
    
    返回:
        绑定状态字典
    """
    supabase = init_supabase()
    
    if supabase is None:
        print("❌ Supabase 未连接")
        return None
    
    try:
        # 使用 name 字段查询（而非 user_id）
        result = supabase.table("users").select("*").eq("name", user_id).execute()
        
        if result.data and len(result.data) > 0:
            profile = result.data[0]
            is_connected = profile.get("drive_connected", False)
            
            if is_connected:
                print(f"✅ {user_id} 已绑定 Google Drive")
                print(f"   邮箱：{profile.get('drive_email') or profile.get('email')}")
                print(f"   Token：{profile.get('drive_access_token')[:30]}..." if profile.get('drive_access_token') else "   Token：无")
            else:
                print(f"⚠️ {user_id} 尚未绑定 Google Drive")
            
            return profile
        else:
            print(f"⚠️ 用户 {user_id} 不存在")
            return None
            
    except Exception as e:
        print(f"❌ 查询失败：{e}")
        return None


def unbind_drive(user_id: str):
    """
    解除 Google Drive 绑定
    
    参数:
        user_id: 用户ID
    
    返回:
        操作结果
    """
    supabase = init_supabase()
    
    if supabase is None:
        print("❌ Supabase 未连接")
        return {"success": False, "error": "Supabase not connected"}
    
    try:
        # 使用 name 字段作为标识
        data = {
            "name": user_id,
            "drive_connected": False,
            "drive_access_token": None,
            "drive_email": None
        }
        
        result = supabase.table("users").upsert(data).execute()
        
        print(f"✅ 已解除 {user_id} 的 Google Drive 绑定")
        return {"success": True}
        
    except Exception as e:
        print(f"❌ 解绑失败：{e}")
        return {"success": False, "error": str(e)}


def get_all_connected_users():
    """
    获取所有已绑定 Google Drive 的用户
    
    返回:
        已绑定用户列表
    """
    supabase = init_supabase()
    
    if supabase is None:
        print("❌ Supabase 未连接")
        return []
    
    try:
        result = supabase.table("users").select("*").eq("drive_connected", True).execute()
        
        if result.data:
            print(f"\n📊 已绑定 Google Drive 的用户数量：{len(result.data)}\n")
            for user in result.data:
                user_name = user.get('name', 'Unknown')
                user_email = user.get('drive_email') or user.get('email', 'N/A')
                print(f"  - {user_name} ({user_email})")
        else:
            print("⚠️ 暂无用户绑定 Google Drive")
        
        return result.data
        
    except Exception as e:
        print(f"❌ 查询失败：{e}")
        return []


# ============================================================
# 测试代码
# ============================================================
if __name__ == "__main__":
    print("🧪 测试 Google Drive 绑定流程模拟器\n")
    
    # 1. 模拟绑定
    print("=" * 60)
    print("1️⃣ 模拟用户绑定 Google Drive")
    print("=" * 60)
    simulate_drive_auth("u_demo", "demo@gmail.com")
    
    print("\n" + "=" * 60)
    print("2️⃣ 检查绑定状态")
    print("=" * 60)
    check_drive_status("u_demo")
    
    print("\n" + "=" * 60)
    print("3️⃣ 获取所有已绑定用户")
    print("=" * 60)
    get_all_connected_users()
    
    print("\n✅ 测试完成！")
