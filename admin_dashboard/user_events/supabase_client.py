"""
Supabase 客户端单例
Supabase Client Singleton
"""

import os
from typing import Optional

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

_client: Optional[Client] = None

def get_client() -> Optional[Client]:
    """获取 Supabase 客户端单例"""
    global _client
    
    if not SUPABASE_AVAILABLE:
        print("⚠️ Supabase SDK 不可用")
        return None
    
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            print("⚠️ 缺少环境变量 SUPABASE_URL 或 SUPABASE_KEY")
            return None
        
        try:
            _client = create_client(url, key)
            print("✅ Supabase 客户端初始化成功")
        except Exception as e:
            print(f"❌ Supabase 客户端初始化失败: {e}")
            return None
    
    return _client
