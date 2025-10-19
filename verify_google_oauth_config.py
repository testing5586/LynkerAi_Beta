#!/usr/bin/env python3
"""
==========================================================
Google OAuth 配置验证工具
==========================================================
验证 Replit Secrets 中的 Google OAuth 密钥是否正确配置
"""

import os
import sys

def verify_oauth_config():
    """验证 Google OAuth 环境变量"""
    
    print("🔍 正在检查 Google OAuth 配置...\n")
    print("=" * 60)
    
    # 需要检查的环境变量
    required_secrets = {
        "VITE_GOOGLE_CLIENT_ID": "Google OAuth Client ID",
        "VITE_GOOGLE_CLIENT_SECRET": "Google OAuth Client Secret",
        "VITE_GOOGLE_REDIRECT_URI": "Google OAuth Redirect URI"
    }
    
    all_configured = True
    
    for key, description in required_secrets.items():
        value = os.getenv(key)
        
        if value:
            # 只显示部分密钥（安全考虑）
            if "SECRET" in key:
                masked_value = value[:10] + "..." + value[-5:] if len(value) > 15 else "***"
            else:
                masked_value = value
            
            print(f"✅ {description}")
            print(f"   Key: {key}")
            print(f"   Value: {masked_value}")
            print()
        else:
            print(f"❌ {description}")
            print(f"   Key: {key}")
            print(f"   Status: 未配置")
            print()
            all_configured = False
    
    print("=" * 60)
    
    if all_configured:
        print("\n🎉 所有 Google OAuth 密钥配置正确！")
        print("\n📝 下一步操作：")
        print("   1. 前端集成 GoogleDriveSyncButton.jsx 组件")
        print("   2. 用户点击按钮完成 OAuth 授权")
        print("   3. 获取 access_token 并存储到 Supabase")
        print("   4. 后端自动同步记忆到 Google Drive")
        return True
    else:
        print("\n⚠️ 部分密钥未配置，请在 Replit Secrets 中添加缺失的密钥")
        return False


def show_oauth_flow():
    """显示 OAuth 授权流程说明"""
    
    print("\n" + "=" * 60)
    print("📚 Google OAuth 2.0 授权流程说明")
    print("=" * 60)
    
    client_id = os.getenv("VITE_GOOGLE_CLIENT_ID")
    redirect_uri = os.getenv("VITE_GOOGLE_REDIRECT_URI")
    
    if client_id and redirect_uri:
        print("\n🔗 OAuth 授权 URL（用户需要访问此链接）：")
        print()
        
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?" \
                   f"client_id={client_id}&" \
                   f"redirect_uri={redirect_uri}&" \
                   f"response_type=code&" \
                   f"scope=https://www.googleapis.com/auth/drive.file&" \
                   f"access_type=offline&" \
                   f"prompt=consent"
        
        print(auth_url)
        print()
        print("📋 授权流程：")
        print("   1. 用户点击上述链接")
        print("   2. 选择 Google 账号并授权")
        print("   3. 重定向回您的应用（带 code 参数）")
        print("   4. 后端用 code 换取 access_token")
        print("   5. 存储 access_token 到 Supabase users 表")
        print()
    else:
        print("\n⚠️ 无法生成授权 URL，请确保已配置 CLIENT_ID 和 REDIRECT_URI")


def test_google_api_connection():
    """测试是否能连接到 Google API"""
    
    print("\n" + "=" * 60)
    print("🔌 测试 Google API 连接...")
    print("=" * 60)
    
    try:
        import requests
        
        response = requests.get("https://www.googleapis.com/drive/v3/about?fields=user", timeout=5)
        
        if response.status_code == 401:
            print("\n✅ Google Drive API 可访问（需要授权）")
            print("   这是预期结果，说明 API 端点正常")
        else:
            print(f"\n📊 响应状态码：{response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n⚠️ 网络连接失败：{e}")
    except ImportError:
        print("\n⚠️ requests 库未安装，跳过 API 连接测试")


if __name__ == "__main__":
    print("🔐 Google OAuth 配置验证工具\n")
    
    # 1. 验证环境变量
    config_ok = verify_oauth_config()
    
    # 2. 显示 OAuth 流程
    if config_ok:
        show_oauth_flow()
    
    # 3. 测试 API 连接
    test_google_api_connection()
    
    print("\n" + "=" * 60)
    print("✅ 验证完成！")
    print("=" * 60)
