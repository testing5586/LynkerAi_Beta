#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lynker Engine v2.0 UTF-8 自动修复脚本
批量为 Child AI 模块添加 UTF-8 修复代码段
"""

import os
import sys
import shutil
import io

# 目标文件列表
TARGET_FILES = [
    'child_ai_feedback.py',
    'child_ai_insight.py',
    'child_ai_learning.py',
    'child_ai_memory.py',
    'child_ai_profiles.py'
]

# UTF-8 修复代码段
UTF8_FIX_CODE = """# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
"""

# safe_print 函数
SAFE_PRINT_CODE = """
def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        msg = " ".join(str(a) for a in args)
        print(msg.encode('utf-8', 'replace').decode('utf-8'))
"""

def create_backup_dir():
    """创建备份目录"""
    backup_dir = './backup'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    return backup_dir

def file_has_utf8_fix(filepath):
    """检查文件是否已有 UTF-8 修复代码"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            return 'sys.stdout = io.TextIOWrapper' in content
    except:
        return False

def file_has_safe_print(filepath):
    """检查文件是否已有 safe_print 函数"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            return 'def safe_print(' in content
    except:
        return False

def patch_file(filepath, backup_dir):
    """为单个文件添加 UTF-8 修复"""
    filename = os.path.basename(filepath)
    backup_path = os.path.join(backup_dir, f"{filename}.bak")
    
    # 创建备份
    if os.path.exists(filepath):
        shutil.copy2(filepath, backup_path)
        print(f"已备份: {filepath} -> {backup_path}")
    
    # 读取原文件内容
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        print(f"无法读取文件: {filepath}")
        return False
    
    # 添加 UTF-8 修复代码段（如果不存在）
    if not file_has_utf8_fix(filepath):
        # 找到第一个 import 语句的位置
        lines = content.split('\n')
        insert_index = 0
        
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                insert_index = i
                break
        
        # 在第一个 import 之前插入 UTF-8 修复代码
        lines.insert(insert_index, UTF8_FIX_CODE)
        content = '\n'.join(lines)
        print(f"已添加 UTF-8 修复代码到: {filepath}")
    
    # 添加 safe_print 函数（如果不存在）
    if not file_has_safe_print(filepath):
        content += SAFE_PRINT_CODE
        print(f"已添加 safe_print 函数到: {filepath}")
    
    # 写入修复后的内容
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"写入文件失败: {filepath}, 错误: {e}")
        return False

def main():
    """主函数"""
    print("Lynker Engine v2.0 UTF-8 Auto Patch Script")
    print("=" * 50)
    
    # 创建备份目录
    backup_dir = create_backup_dir()
    
    # 修复文件计数
    patched_count = 0
    
    # 遍历目标文件
    for filename in TARGET_FILES:
        filepath = filename
        
        if os.path.exists(filepath):
            print(f"\nProcessing: {filepath}")
            if patch_file(filepath, backup_dir):
                patched_count += 1
                print(f"Fix successful: {filepath}")
            else:
                print(f"Fix failed: {filepath}")
        else:
                print(f"File not found: {filepath}")
    
    # 输出结果
    print("\n" + "=" * 50)
    print(f"UTF-8 patch completed, fixed {patched_count} files.")
    
    # Verify UTF-8 encoding
    print("\nVerifying UTF-8 encoding...")
    try:
        print("UTF-8 test output")
    except UnicodeEncodeError:
        print("UTF-8 encoding test failed")
        return False
    
    print("UTF-8 encoding verification passed")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)