import os
import sys
from openai import OpenAI
from supabase import create_client, Client
from replit_bridge import write_file, run_command

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def check_environment():
    print("🔧 LynkerAI 环境检查")
    print("=" * 50)
    
    if os.getenv("OPENAI_API_KEY"):
        print("✓ OpenAI API key found")
    else:
        print("⚠ OpenAI API key not set")
        return False
    
    if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"):
        print("✓ Supabase credentials found")
    else:
        print("⚠ Supabase credentials not set (optional)")
    
    print("=" * 50)
    return True

def instruct_and_execute(task_description: str):
    print(f"\n🚀 开始执行任务: {task_description}\n")
    
    prompt = f"""
    你是 LynkerAi 的总AI。请为以下任务生成代码文件。

    请严格按照以下格式输出：
    
    文件名：<filename>
    内容：
    ```
    <code content here>
    ```
    
    任务：{task_description}
    
    注意：
    - 文件名必须写在"文件名："后面
    - 代码内容必须写在```代码块中
    - 如果需要安装Python依赖，使用格式：依赖：package1 package2（不要用pip install，系统会自动处理）
    """
    
    try:
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        
        if not res.choices:
            print("⚠️ OpenAI未返回任何响应")
            return
        
        output = res.choices[0].message.content
        
        if not output:
            print("⚠️ 没有收到AI响应")
            return
        
        print("🧠 总AI输出：")
        print("=" * 50)
        print(output)
        print("=" * 50)
        
        import re
        
        dependencies = re.findall(r'(?:依赖[：:]\s*|pip install\s+|uv add\s+)([^\n]+)', output)
        if dependencies:
            for deps in dependencies:
                raw_packages = deps.strip()
                
                if not raw_packages or raw_packages.lower() in ['无', 'none', 'n/a', '不需要', '无需']:
                    continue
                
                if any(char in raw_packages for char in ['&', '|', ';', '`', '$']):
                    print(f"⚠️ 跳过不安全的依赖: {raw_packages}")
                    continue
                
                packages = re.sub(r'[（）]', '', raw_packages)
                packages = re.sub(r'，|、', ' ', packages)
                packages = ' '.join(packages.split())
                
                valid_packages = []
                for pkg in packages.split():
                    if re.match(r'^[a-zA-Z0-9_-]+(\[[a-zA-Z0-9_,-]+\])?(==|>=|<=|~=|!=|<|>)?[a-zA-Z0-9._,<>!=~-]*$', pkg):
                        valid_packages.append(pkg)
                    elif pkg.strip():
                        print(f"⚠️ 跳过无效的包名: {pkg}")
                
                if valid_packages:
                    packages_str = ' '.join(valid_packages)
                    print(f"\n📦 安装依赖: {packages_str}")
                    run_command(f"uv add {packages_str}")
                else:
                    print(f"⚠️ 未找到有效的包名: {raw_packages}")
        
        filename_match = re.search(r'文件名[：:]\s*[`"]?([^`"\n]+)[`"]?', output)
        if filename_match:
            filename = filename_match.group(1).strip()
            
            code_blocks = re.findall(r'```(?:python)?\s*\n(.*?)```', output, re.DOTALL)
            if code_blocks:
                content = code_blocks[0].strip()
                content = re.sub(r'^依赖[：:][^\n]+\n*', '', content, flags=re.MULTILINE)
                write_file(filename, content)
                print(f"\n✅ 成功创建文件: {filename}")
            else:
                print("⚠️ 未找到代码块")
        else:
            print("⚠️ 未找到文件名")
            
    except Exception as e:
        print(f"❌ 错误: {str(e)}")

def main():
    if not check_environment():
        print("\n❌ 环境配置不完整，请设置 OPENAI_API_KEY")
        sys.exit(1)
    
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
        instruct_and_execute(task)
    else:
        print("\n📖 使用方法:")
        print("  python lynker_master_ai.py '你的任务描述'")
        print("\n示例:")
        print("  python lynker_master_ai.py '创建一个计算器应用'")
        print("  python lynker_master_ai.py '生成一个TODO列表程序'")

if __name__ == "__main__":
    main()
