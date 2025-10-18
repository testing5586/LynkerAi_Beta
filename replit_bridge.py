import os
import subprocess

def write_file(filename, content):
    """写入文件到 Replit"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ 文件 {filename} 已生成。")

def run_command(cmd):
    """执行命令并返回输出"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print("📤 执行结果：\n", result.stdout or result.stderr)
