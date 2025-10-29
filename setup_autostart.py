#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
设置 LynkerAI 开机自动启动
Setup LynkerAI to start automatically with Windows
"""

import os
import sys
import winreg
import getpass

def create_startup_shortcut():
    """创建开机启动项"""
    try:
        # Get current user's startup folder
        startup_folder = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        
        # Get current directory
        current_dir = os.getcwd()
        batch_file = os.path.join(current_dir, 'Start LynkerAI.bat')
        
        # Create a VBS script to run the batch file silently
        vbs_script = f"""
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "{batch_file}" & chr(34), 0
Set WshShell = Nothing
"""
        
        vbs_file = os.path.join(current_dir, 'lynkerai_autostart.vbs')
        with open(vbs_file, 'w', encoding='utf-8') as f:
            f.write(vbs_script)
        
        # Add to Windows registry startup
        key = winreg.HKEY_CURRENT_USER
        subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_WRITE) as registry_key:
            winreg.SetValueEx(registry_key, "LynkerAI", 0, winreg.REG_SZ, vbs_file)
        
        print("✅ Successfully added LynkerAI to Windows startup")
        print(f"   - VBS script created at: {vbs_file}")
        print(f"   - Registry entry added for current user: {getpass.getuser()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to setup autostart: {str(e)}")
        return False

def remove_startup_shortcut():
    """移除开机启动项"""
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_WRITE) as registry_key:
            try:
                winreg.DeleteValue(registry_key, "LynkerAI")
                print("✅ Successfully removed LynkerAI from Windows startup")
                return True
            except WindowsError:
                print("⚠️ LynkerAI was not in startup registry")
                return True
                
    except Exception as e:
        print(f"❌ Failed to remove autostart: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 LynkerAI Autostart Setup Tool")
    print("=" * 60)
    print()
    print("This tool will add LynkerAI to Windows startup.")
    print("LynkerAI will automatically start when you log in to Windows.")
    print()
    
    while True:
        choice = input("Choose an option:\n"
                     "1. Add LynkerAI to Windows startup\n"
                     "2. Remove LynkerAI from Windows startup\n"
                     "3. Exit\n"
                     "Enter your choice (1-3): ").strip()
        
        if choice == '1':
            print("\n🔧 Adding LynkerAI to startup...")
            if create_startup_shortcut():
                print("\n✅ LynkerAI will now start automatically with Windows!")
                print("   - To test, restart your computer")
                print("   - LynkerAI will start in the background")
                print("   - Check your system tray for the Python process")
            break
            
        elif choice == '2':
            print("\n🗑️ Removing LynkerAI from startup...")
            if remove_startup_shortcut():
                print("\n✅ LynkerAI will no longer start automatically")
            break
            
        elif choice == '3':
            print("\n👋 Exiting...")
            break
            
        else:
            print("\n❌ Invalid choice. Please enter 1, 2, or 3.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()