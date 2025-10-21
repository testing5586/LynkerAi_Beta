#!/usr/bin/env python3
"""
==========================================================
自动检测 Replit 域名并更新 OAuth 重定向 URI
==========================================================
功能：
1. 动态检测当前 Replit 公共域名
2. 显示建议的重定向 URI
3. 提供更新指南（手动更新到 Replit Secrets）
4. 可选：通过 Google Cloud API 更新 OAuth 客户端
"""

import os
import sys
import requests
from urllib.parse import urlparse


def detect_replit_domain():
    """检测当前 Replit 域名"""
    
    # 方法 1: 从环境变量读取
    replit_domains = os.getenv('REPLIT_DOMAINS')
    if replit_domains:
        domains = replit_domains.split(',')
        if domains:
            return f"https://{domains[0].strip()}"
    
    # 方法 2: 从 REPLIT_DEV_DOMAIN 读取
    dev_domain = os.getenv('REPLIT_DEV_DOMAIN')
    if dev_domain:
        return f"https://{dev_domain}"
    
    # 方法 3: 构建域名（Sisko 格式）
    repl_id = os.getenv('REPL_ID')
    repl_slug = os.getenv('REPL_SLUG')
    repl_owner = os.getenv('REPL_OWNER')
    
    if repl_id:
        # Sisko 域名格式
        return f"https://{repl_id}.sisko.replit.dev"
    elif repl_slug and repl_owner:
        # 传统域名格式
        return f"https://{repl_slug}.{repl_owner}.repl.co"
    
    return None


def get_current_redirect_uri():
    """获取当前配置的重定向 URI"""
    return os.getenv('VITE_GOOGLE_REDIRECT_URI')


def suggest_redirect_uri(domain):
    """建议的重定向 URI"""
    if not domain:
        return None
    
    # 移除末尾的斜杠
    domain = domain.rstrip('/')
    
    # 返回根路径作为重定向 URI
    return f"{domain}/"


def display_update_guide(current_uri, suggested_uri):
    """显示更新指南"""
    
    print("=" * 60)
    print("🔍 域名检测结果")
    print("=" * 60)
    print()
    
    if current_uri:
        print(f"📌 当前重定向 URI:")
        print(f"   {current_uri}")
    else:
        print("⚠️ 未设置 VITE_GOOGLE_REDIRECT_URI")
    
    print()
    
    if suggested_uri:
        print(f"✅ 建议的重定向 URI:")
        print(f"   {suggested_uri}")
    else:
        print("❌ 无法检测到 Replit 域名")
        return
    
    print()
    print("=" * 60)
    print("📝 更新步骤")
    print("=" * 60)
    print()
    
    # 检查是否需要更新
    if current_uri == suggested_uri:
        print("✅ 当前配置正确，无需更新！")
        return
    
    print("🔧 请按以下步骤更新重定向 URI：")
    print()
    
    print("1️⃣ 更新 Replit Secrets")
    print("   ────────────────────────────────────")
    print("   - 在 Replit 左侧菜单点击 'Secrets' (🔒)")
    print(f"   - 找到 VITE_GOOGLE_REDIRECT_URI")
    print(f"   - 更新为：{suggested_uri}")
    print()
    
    print("2️⃣ 更新 Google Cloud Console")
    print("   ────────────────────────────────────")
    print("   - 访问：https://console.cloud.google.com/")
    print("   - 进入 'APIs & Services' → 'Credentials'")
    print("   - 点击您的 OAuth 2.0 客户端 ID")
    print("   - 在 'Authorized redirect URIs' 中添加：")
    print(f"     {suggested_uri}")
    print()
    
    print("3️⃣ 重启服务")
    print("   ────────────────────────────────────")
    print("   - 更新完成后，重启 Flask API workflow")
    print()
    
    print("=" * 60)
    print()


def check_domain_accessibility(domain):
    """检查域名是否可访问"""
    
    if not domain:
        return False
    
    try:
        response = requests.get(f"{domain}/health", timeout=5)
        return response.status_code == 200
    except:
        try:
            # 尝试访问根路径
            response = requests.get(domain, timeout=5)
            return response.status_code in [200, 404]  # 404 也表示可访问
        except:
            return False


def auto_update_google_oauth(client_id, client_secret, redirect_uri):
    """
    自动更新 Google OAuth 客户端（需要额外凭证）
    
    注意：此功能需要 Google Cloud 服务账号凭证
    """
    
    print("⚠️ 自动更新 Google Cloud OAuth 客户端需要：")
    print("   1. Google Cloud 服务账号密钥")
    print("   2. OAuth 客户端配置 API 访问权限")
    print()
    print("💡 建议：手动在 Google Cloud Console 更新更安全")
    print()
    
    return False


def main():
    """主函数"""
    
    print("=" * 60)
    print("🔐 Replit OAuth 重定向 URI 自动更新工具")
    print("=" * 60)
    print()
    
    # 1. 检测当前域名
    print("🔍 Step 1: 检测 Replit 域名...")
    detected_domain = detect_replit_domain()
    
    if detected_domain:
        print(f"✅ 检测到域名：{detected_domain}")
    else:
        print("❌ 无法检测到 Replit 域名")
        print()
        print("请确保您在 Replit 环境中运行此脚本。")
        sys.exit(1)
    
    print()
    
    # 2. 检查域名可访问性
    print("🔍 Step 2: 检查域名可访问性...")
    if check_domain_accessibility(detected_domain):
        print(f"✅ 域名可访问")
    else:
        print(f"⚠️ 域名暂时无法访问（这是正常的，服务可能还在启动）")
    
    print()
    
    # 3. 获取当前和建议的重定向 URI
    current_uri = get_current_redirect_uri()
    suggested_uri = suggest_redirect_uri(detected_domain)
    
    # 4. 显示更新指南
    display_update_guide(current_uri, suggested_uri)
    
    # 5. 询问是否需要帮助
    print("━" * 60)
    print()
    print("📋 可用选项：")
    print()
    print("   A. 手动更新（推荐）")
    print("      - 按照上述步骤手动更新")
    print("      - 最安全、最可靠")
    print()
    print("   B. 复制重定向 URI")
    print("      - 复制建议的 URI 并手动粘贴")
    print()
    print("   C. 查看环境变量详情")
    print("      - 显示所有相关环境变量")
    print()
    
    choice = input("请选择 (A/B/C) 或按 Enter 退出：").strip().upper()
    
    if choice == 'A':
        print()
        print("✅ 请按照上述步骤手动更新重定向 URI")
    elif choice == 'B':
        print()
        print("=" * 60)
        print("📋 请复制以下 URI：")
        print("=" * 60)
        print()
        print(suggested_uri)
        print()
        print("=" * 60)
    elif choice == 'C':
        print()
        print("=" * 60)
        print("📊 环境变量详情")
        print("=" * 60)
        print()
        print(f"REPLIT_DOMAINS: {os.getenv('REPLIT_DOMAINS', 'NOT_SET')}")
        print(f"REPLIT_DEV_DOMAIN: {os.getenv('REPLIT_DEV_DOMAIN', 'NOT_SET')}")
        print(f"REPL_ID: {os.getenv('REPL_ID', 'NOT_SET')}")
        print(f"REPL_SLUG: {os.getenv('REPL_SLUG', 'NOT_SET')}")
        print(f"REPL_OWNER: {os.getenv('REPL_OWNER', 'NOT_SET')}")
        print(f"VITE_GOOGLE_CLIENT_ID: {os.getenv('VITE_GOOGLE_CLIENT_ID', 'NOT_SET')[:20]}...")
        print(f"VITE_GOOGLE_REDIRECT_URI: {os.getenv('VITE_GOOGLE_REDIRECT_URI', 'NOT_SET')}")
        print()
    
    print()
    print("🎉 完成！")


if __name__ == "__main__":
    main()
