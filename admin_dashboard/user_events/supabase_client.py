# -*- coding: utf-8 -*-
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
        print("Warning: Supabase SDK not available")
        return None
    
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            print("Warning: Missing environment variables SUPABASE_URL or SUPABASE_KEY")
            return None
        
        try:
            _client = create_client(url, key)
            print("OK: Supabase client initialized successfully")
        except Exception as e:
            print(f"ERROR: Supabase client initialization failed: {e}")
            return None
    
    return _client
