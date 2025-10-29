# -*- coding: utf-8 -*-
import os
import hashlib
from dotenv import load_dotenv
# Try to load .env from multiple possible locations
load_dotenv(dotenv_path='../.env')
load_dotenv(dotenv_path='.env')
load_dotenv()

MASTER_KEY = os.getenv("MASTER_VAULT_KEY")
if not MASTER_KEY:
    raise ValueError("MASTER_VAULT_KEY environment variable must be set for authentication")

def verify_login(password):
    token = hashlib.sha256(MASTER_KEY.encode()).hexdigest()[:16]
    print(f"DEBUG: MASTER_KEY={MASTER_KEY}")
    print(f"DEBUG: Expected token={token}")
    print(f"DEBUG: Received password={password}")
    print(f"DEBUG: Password match={password == token}")
    return password == token

def get_access_token():
    """生成访问令牌供用户使用"""
    return hashlib.sha256(MASTER_KEY.encode()).hexdigest()[:16]
