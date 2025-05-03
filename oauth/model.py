import jwt
import hashlib

SECRET_KEY = "b07704a225c3866836d15389ae695bfcd19fdb2b7af52fde1e33ff27d1c3f52f"
ALGORITHM = "HS256"

def createAuthToken(data: dict) -> str:
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decodeAuthToken(token: str) -> dict:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload

def encodePassword(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()