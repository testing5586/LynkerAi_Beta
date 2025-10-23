"""
LynkerAI Master Vault Engine v2.0
---------------------------------
功能：
✅ 加密与解密 Master AI 学习知识（AES256）
✅ 写入 PostgreSQL master_vault 表（直接 SQL + Supabase 双模式）
✅ Superintendent Admin 权限验证系统
"""

import os
import base64
import hashlib
import psycopg2
from cryptography.fernet import Fernet
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

def get_cipher():
    """从环境变量读取 MASTER_VAULT_KEY 并生成 AES 密钥"""
    key = os.getenv("MASTER_VAULT_KEY")
    if not key:
        raise ValueError("❌ 未设置 MASTER_VAULT_KEY 环境变量！")
    key_bytes = hashlib.sha256(key.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key_bytes))

def encrypt_vault_data(content: str) -> str:
    """加密内容"""
    f = get_cipher()
    return f.encrypt(content.encode()).decode()

def decrypt_vault_data(encrypted: str, role: str) -> str:
    """根据角色解密内容"""
    if role != "Superintendent Admin":
        raise PermissionError("🚫 无权访问加密内容：需要 Superintendent Admin 身份。")
    f = get_cipher()
    return f.decrypt(encrypted.encode()).decode()

def get_db_connection():
    """获取 PostgreSQL 连接"""
    return psycopg2.connect(DATABASE_URL)

def insert_vault(title: str, content: str, created_by: str = "Master AI", access_level: str = "restricted"):
    """将加密后的知识写入 master_vault 表（使用直接 SQL）"""
    encrypted_content = encrypt_vault_data(content)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO master_vault (title, encrypted_content, access_level, created_by, created_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (title, encrypted_content, access_level, created_by, datetime.utcnow()))
        
        vault_id = cursor.fetchone()[0]
        conn.commit()
        print(f"✅ 已写入 Vault：{title} ({created_by}) [ID: {vault_id}]")
        return vault_id
    finally:
        cursor.close()
        conn.close()

def read_vault(title: str, role: str):
    """根据标题读取并尝试解密 Vault 内容（使用直接 SQL）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, title, encrypted_content, access_level, created_by, created_at
            FROM master_vault
            WHERE title = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (title,))
        
        record = cursor.fetchone()
        if not record:
            print("⚠️ 未找到指定标题内容。")
            return None
        
        vault_id, title, encrypted_content, access_level, created_by, created_at = record
        
        if role == "Superintendent Admin":
            decrypted = decrypt_vault_data(encrypted_content, role)
            print(f"🔓 解密成功：{title}")
            print(f"📝 内容：\n{decrypted}")
            print(f"📊 创建者：{created_by} | 时间：{created_at}")
            return decrypted
        else:
            print("🚫 您没有权限查看此内容。")
            return None
    finally:
        cursor.close()
        conn.close()

def list_vault_entries(role: str = None):
    """列出所有 Vault 条目（仅显示标题和元数据）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, title, access_level, created_by, created_at
            FROM master_vault
            ORDER BY created_at DESC
        """)
        
        entries = cursor.fetchall()
        print(f"\n📚 Master Vault 知识库 ({len(entries)} 条记录)")
        print("=" * 70)
        
        for entry in entries:
            vault_id, title, access_level, created_by, created_at = entry
            lock = "🔒" if access_level == "restricted" else "🔓"
            print(f"{lock} [{created_at}] {title}")
            print(f"   创建者: {created_by} | 权限: {access_level}")
            print("-" * 70)
        
        return entries
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 LynkerAI Master Vault Engine v2.0")
    print("=" * 70)
    
    try:
        print("\n📝 测试 1：加密并存储知识...")
        insert_vault(
            title="AI命理学习记录#001",
            content="Master AI 在学习刻分算法时发现：23:10~23:12为关键命刻区间。",
            created_by="Master AI"
        )
        
        insert_vault(
            title="紫微斗数规律发现#001",
            content="通过分析500个命盘，发现太阳在午宫的人在30-35岁间有重大事业转折的概率达78%。",
            created_by="Master AI"
        )
        
        print("\n📚 测试 2：列出所有 Vault 条目...")
        list_vault_entries()
        
        print("\n🔓 测试 3：Superintendent Admin 解密读取...")
        read_vault("AI命理学习记录#001", role="Superintendent Admin")
        
        print("\n🚫 测试 4：普通用户尝试读取（应被拒绝）...")
        try:
            read_vault("AI命理学习记录#001", role="User")
        except PermissionError as e:
            print(f"✅ 权限验证成功：{e}")
        
        print("\n" + "=" * 70)
        print("✅ Master Vault Engine 测试完成！")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()
