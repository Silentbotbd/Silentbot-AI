from datetime import datetime, timedelta
from typing import Optional, Union
import hashlib
import os
import secrets
import json
import base64
import hmac

SECRET_KEY = os.getenv("SECRET_KEY", "DEFAULT_SECRET_CHANGE_ME")

def get_password_hash(password: str) -> str:
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + ":" + key.hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        salt_hex, key_hex = hashed_password.split(":")
        salt = bytes.fromhex(salt_hex)
        new_key = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100000)
        return new_key.hex() == key_hex
    except: return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
    to_encode.update({"exp": expire.timestamp()})
    header = {"alg": "HS256", "typ": "JWT"}
    h = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    p = base64.urlsafe_b64encode(json.dumps(to_encode).encode()).decode().rstrip("=")
    m = f"{h}.{p}"
    sig = hmac.new(SECRET_KEY.encode(), m.encode(), hashlib.sha256).digest()
    s = base64.urlsafe_b64encode(sig).decode().rstrip("=")
    return f"{m}.{s}"

def decode_token(token: str):
    try:
        h, p, s = token.split(".")
        m = f"{h}.{p}"
        sig = hmac.new(SECRET_KEY.encode(), m.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(s, base64.urlsafe_b64encode(sig).decode().rstrip("=")): return None
        payload = json.loads(base64.urlsafe_b64decode(p + "==").decode())
        if datetime.utcnow().timestamp() > payload.get("exp", 0): return None
        return payload
    except: return None
