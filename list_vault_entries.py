from master_vault_engine import list_vault_entries, read_vault
import os

def main():
    print("📚 Master Vault 知识库浏览器")
    print("=" * 50)
    
    # 检查身份
    role = os.getenv("USER_ROLE", "User")
    print(f"🔑 当前身份: {role}\n")

    # 获取 Vault 条目
    entries = list_vault_entries()
    if not entries:
        print("⚠️ 暂无记录。")
        return

    print("📖 当前 Vault 条目:")
    print("-" * 50)
    for i, e in enumerate(entries, start=1):
        vault_id, title, access_level, created_by, created_at = e
        print(f"{i}. {title}  |  创建者: {created_by}  |  时间: {created_at}")
    print("-" * 50)

    # 仅管理员可查看内容
    if role == "Superintendent Admin":
        try:
            choice = input("\n请输入要解密查看的条目序号（或按 Enter 跳过）：")
            if choice.strip():
                index = int(choice) - 1
                vault_id, title, access_level, created_by, created_at = entries[index]
                print("\n🔓 解密中...\n")
                content = read_vault(title, role=role)
                print(f"📜 {title} 内容：\n{content}")
        except Exception as e:
            print(f"❌ 错误: {e}")
    else:
        print("\n🚫 您没有解密权限。仅 Superintendent Admin 可查看内容。")

if __name__ == "__main__":
    main()
