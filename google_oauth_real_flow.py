#!/usr/bin/env python3
"""
==========================================================
Google OAuth 2.0 真实授权流程
==========================================================
功能：
1. 生成真实的 Google OAuth 授权 URL
2. 接收授权回调
3. 用授权码换取 access_token
4. 保存到 Supabase users 表
"""

import os
import sys
import requests
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse
from supabase_init import init_supabase


def get_oauth_config():
    """读取 OAuth 配置"""
    config = {
        'client_id': os.getenv('VITE_GOOGLE_CLIENT_ID'),
        'client_secret': os.getenv('VITE_GOOGLE_CLIENT_SECRET'),
        'redirect_uri': os.getenv('VITE_GOOGLE_REDIRECT_URI')
    }
    
    # 验证配置
    missing = [k for k, v in config.items() if not v]
    if missing:
        print(f"❌ 缺少必需的环境变量：{', '.join(missing)}")
        print("\n请在 Replit Secrets 中配置以下密钥：")
        print("  - VITE_GOOGLE_CLIENT_ID")
        print("  - VITE_GOOGLE_CLIENT_SECRET")
        print("  - VITE_GOOGLE_REDIRECT_URI")
        sys.exit(1)
    
    return config


def generate_auth_url(config):
    """生成 OAuth 授权 URL"""
    
    # OAuth 2.0 授权端点
    auth_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
    
    # 授权参数
    params = {
        'client_id': config['client_id'],
        'redirect_uri': config['redirect_uri'],
        'response_type': 'code',
        'scope': ' '.join([
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/userinfo.email',
            'openid'
        ]),
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    auth_url = f"{auth_endpoint}?{urlencode(params)}"
    
    return auth_url


def exchange_code_for_token(auth_code, config):
    """用授权码换取 access_token"""
    
    token_endpoint = "https://oauth2.googleapis.com/token"
    
    token_data = {
        'code': auth_code,
        'client_id': config['client_id'],
        'client_secret': config['client_secret'],
        'redirect_uri': config['redirect_uri'],
        'grant_type': 'authorization_code'
    }
    
    try:
        response = requests.post(token_endpoint, data=token_data)
        
        if response.status_code == 200:
            token_info = response.json()
            return {
                'success': True,
                'access_token': token_info.get('access_token'),
                'refresh_token': token_info.get('refresh_token'),
                'expires_in': token_info.get('expires_in'),
                'id_token': token_info.get('id_token')
            }
        else:
            return {
                'success': False,
                'error': f"Token 交换失败：{response.status_code}",
                'details': response.text
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def get_user_info(access_token):
    """获取用户信息（邮箱）- 使用 v1 API"""
    
    try:
        response = requests.get(
            'https://www.googleapis.com/oauth2/v1/userinfo?alt=json',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if response.status_code == 200:
            user_info = response.json()
            return {
                'success': True,
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'picture': user_info.get('picture')
            }
        else:
            return {'success': False, 'error': '获取用户信息失败'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def save_to_supabase(user_id, access_token, refresh_token, user_email):
    """保存 token 到 Supabase users 表"""
    
    supabase = init_supabase()
    
    if supabase is None:
        return {'success': False, 'error': 'Supabase 未连接'}
    
    try:
        from datetime import datetime
        
        # 更新用户的 Google Drive 绑定信息
        result = supabase.table('users').update({
            'drive_connected': True,
            'drive_access_token': access_token,
            'drive_refresh_token': refresh_token,
            'drive_email': user_email,
            'updated_at': datetime.now().isoformat()
        }).eq('name', user_id).execute()
        
        if result.data:
            return {'success': True, 'data': result.data}
        else:
            return {'success': False, 'error': '更新失败'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}


def run_oauth_flow(user_id=None):
    """运行完整的 OAuth 授权流程"""
    
    print("=" * 60)
    print("🔐 Google OAuth 2.0 真实授权流程")
    print("=" * 60)
    print()
    
    # 1. 读取配置
    print("📋 Step 1: 读取 OAuth 配置...")
    config = get_oauth_config()
    print(f"✅ Client ID: {config['client_id'][:20]}...")
    print(f"✅ Redirect URI: {config['redirect_uri']}")
    print()
    
    # 2. 生成授权 URL
    print("🔗 Step 2: 生成授权 URL...")
    auth_url = generate_auth_url(config)
    print()
    print("=" * 60)
    print("📌 请复制以下 URL 到浏览器打开并授权：")
    print("=" * 60)
    print()
    print(auth_url)
    print()
    print("=" * 60)
    print("完成后复制浏览器地址栏中的 code 参数，粘贴回控制台。")
    print("=" * 60)
    print()
    
    # 4. 获取授权码
    auth_code = input("🔑 请输入授权码（code 参数的值）：").strip()
    
    if not auth_code:
        print("❌ 未输入授权码，退出流程")
        return
    
    print()
    print("🔄 Step 3: 用授权码换取 access_token...")
    
    # 5. 换取 token
    token_result = exchange_code_for_token(auth_code, config)
    
    if not token_result['success']:
        print(f"❌ Token 交换失败：{token_result.get('error')}")
        if token_result.get('details'):
            print(f"   详情：{token_result['details']}")
        return
    
    access_token = token_result['access_token']
    refresh_token = token_result.get('refresh_token')
    
    print(f"✅ Access Token: {access_token[:20]}...")
    if refresh_token:
        print(f"✅ Refresh Token: {refresh_token[:20]}...")
    print()
    
    # 6. 获取用户信息
    print("👤 Step 4: 获取用户信息...")
    user_info_result = get_user_info(access_token)
    
    if not user_info_result['success']:
        print(f"⚠️ 获取用户信息失败：{user_info_result.get('error')}")
        user_email = "未知"
    else:
        user_email = user_info_result.get('email')
        print(f"✅ 用户邮箱：{user_email}")
        print(f"✅ 用户名称：{user_info_result.get('name')}")
    print()
    
    # 7. 保存到 Supabase
    if user_id:
        print(f"💾 Step 5: 保存到 Supabase.users...")
        save_result = save_to_supabase(user_id, access_token, refresh_token, user_email)
        
        if save_result['success']:
            print()
            print("=" * 60)
            print("✅ 授权成功！")
            print(f"📧 邮箱：{user_email}")
            print(f"🔑 Token：{access_token[:10]}...")
            print("💾 已保存到 Supabase.users")
            print("=" * 60)
            print()
        else:
            print(f"⚠️ 保存失败：{save_result.get('error')}")
            print()
    else:
        print("⚠️ 未提供 user_id，跳过保存到 Supabase")
        print()
        print("💡 如需保存，请运行：")
        print(f'   python google_oauth_real_flow.py --user-id=u_demo')
        print()
    
    # 8. 测试 Google Drive 连接
    if user_id:
        print("🧪 测试 Google Drive 连接...")
        
        from google_drive_sync import test_google_drive_connection
        
        if test_google_drive_connection(access_token):
            print("✅ Google Drive 连接测试成功！")
        else:
            print("⚠️ Google Drive 连接测试失败")
        
        print()
        print("📊 下一步操作：")
        print("   1. 生成子AI记忆：python child_ai_memory.py")
        print("   2. 记忆会自动同步到 Google Drive")
        print()
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user_email': user_email
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Google OAuth 2.0 真实授权流程')
    parser.add_argument('--user-id', type=str, help='用户ID（用于保存到 Supabase）')
    
    args = parser.parse_args()
    
    run_oauth_flow(user_id=args.user_id)
