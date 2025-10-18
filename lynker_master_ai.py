import os
from openai import OpenAI
from supabase import create_client, Client

def main():
    print("Python environment ready!")
    print("Packages installed: openai, supabase")
    print("\nTo use OpenAI, set your OPENAI_API_KEY environment variable")
    print("To use Supabase, set SUPABASE_URL and SUPABASE_KEY environment variables")
    
    # Example: Check if API keys are configured
    if os.getenv("OPENAI_API_KEY"):
        print("\n✓ OpenAI API key found")
    else:
        print("\n⚠ OpenAI API key not set")
    
    if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"):
        print("✓ Supabase credentials found")
    else:
        print("⚠ Supabase credentials not set")

if __name__ == "__main__":
    main()

from replit_bridge import write_file, run_command
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def instruct_and_execute(task_description):
    prompt = f"""
    你是 LynkerAi 的总AI。请为以下任务生成：
    1. 文件名
    2. 文件内容
    3. 若需要安装依赖，请写出命令
    任务：{task_description}
    """
    res = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": prompt}]
    )
    output = res.choices[0].message.content

    # 简单解析输出（假设AI生成了“文件名：xxx\n内容：...”）
    if "文件名" in output and "内容" in output:
        filename = output.split("文件名：")[1].split("\n")[0].strip()
        content = output.split("内容：")[1].strip()
        write_file(filename, content)

    if "pip install" in output:
        cmd = output.split("pip install")[1].split("\n")[0]
        run_command(f"pip install {cmd}")

    print("🧠 总AI输出：\n", output)
