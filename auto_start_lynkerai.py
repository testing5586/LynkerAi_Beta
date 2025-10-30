#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LynkerAI 自动启动脚本
Automatically initializes database and starts the application
"""

import os
import sys
import time
import subprocess
import webbrowser
from dotenv import load_dotenv

# Set console encoding for Windows
if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def check_and_setup_database():
    """检查并设置数据库"""
    print("🔍 Checking database setup...")
    
    try:
        # Run the auto-setup script
        result = subprocess.run([sys.executable, 'auto_setup_supabase.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database setup completed successfully")
            return True
        else:
            print(f"⚠️ Database setup had issues: {result.stderr}")
            # Continue anyway as the app might still work
            return True
    except Exception as e:
        print(f"⚠️ Could not run database setup: {str(e)}")
        return True  # Continue anyway

def calculate_login_password():
    """计算登录密码"""
    load_dotenv()
    master_key = os.getenv("MASTER_VAULT_KEY", "$8wYt7RzQ4pBm9HcL2xFs0NeKaGdJqVu")
    
    import hashlib
    password = hashlib.sha256(master_key.encode()).hexdigest()[:16]
    return password

def start_application():
    """启动应用程序"""
    print("\n🚀 Starting LynkerAI application...")
    
    # Start the Flask app
    try:
        # Use run_app.bat if it exists, otherwise start directly
        if os.path.exists('run_app.bat'):
            process = subprocess.Popen(['run_app.bat'], shell=True)
        else:
            process = subprocess.Popen([
                sys.executable, 'admin_dashboard/app.py'
            ])
        
        # Wait a bit for the server to start
        time.sleep(3)
        
        # Open browser automatically
        password = calculate_login_password()
        url = "http://localhost:5000/admin"
        
        print(f"\n🌐 Opening browser at {url}")
        print(f"🔑 Login password: {password}")
        
        webbrowser.open(url)
        
        print("\n✅ LynkerAI is now running!")
        print("   - The browser should open automatically")
        print("   - If not, navigate to http://localhost:5000/admin")
        print(f"   - Login with password: {password}")
        print("\n   Press Ctrl+C in this window to stop the server")
        
        # Keep the script running
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping LynkerAI...")
            process.terminate()
            
    except Exception as e:
        print(f"❌ Failed to start application: {str(e)}")
        sys.exit(1)

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 LynkerAI Auto-Start Tool")
    print("=" * 60)
    
    # 1. Check and setup database
    check_and_setup_database()
    
    # 2. Start application
    start_application()

if __name__ == "__main__":
    main()