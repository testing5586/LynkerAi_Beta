import os
import hashlib

MASTER_KEY = os.getenv("MASTER_VAULT_KEY", "default_key")

def verify_login(password):
    token = hashlib.sha256(MASTER_KEY.encode()).hexdigest()[:16]
    return password == token

def get_access_token():
    """生成访问令牌供用户使用"""
    return hashlib.sha256(MASTER_KEY.encode()).hexdigest()[:16]
