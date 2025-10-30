import os
import hashlib
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

key = os.getenv("MASTER_VAULT_KEY", "")
print(hashlib.sha256(key.encode()).hexdigest()[:16])

