import os
import hashlib

MASTER_KEY = os.getenv("MASTER_VAULT_KEY")
if not MASTER_KEY:
    raise ValueError("MASTER_VAULT_KEY environment variable must be set for authentication")

def verify_login(password):
    token = hashlib.sha256(MASTER_KEY.encode()).hexdigest()[:16]
    return password == token

def get_access_token():
    """生成访问令牌供用户使用"""
    return hashlib.sha256(MASTER_KEY.encode()).hexdigest()[:16]
