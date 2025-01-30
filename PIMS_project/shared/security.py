from passlib.context import CryptContext
from datetime import timedelta, datetime
from jose import jwt, JWTError
import os, time, random, string
from starlette import status
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from shared.database import get_db
from sqlalchemy.orm import Session
from itsdangerous import URLSafeTimedSerializer
from Users.model.models import Users
from hashlib import sha256

ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")
serializer = URLSafeTimedSerializer(SECRET_KEY)
DEBUG_MODE = os.getenv("DEBUG", "False") == "True"
outh2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')

def create_token(data: dict):
    
    payload = {
        "sub": data["sub"],  
        "email": data["email"], 
        "iat": int(time.time()),  
        "exp": datetime.utcnow() + timedelta(hours=1)  
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def user_access(token:str = Depends(outh2_bearer), session: Session=Depends(get_db)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
             raise credentials_exception

    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Permission denied to perform this operation on the selected account.") 
    
    user = session.query(Users).filter(Users.username == username).first()
    if user is None:
        raise credentials_exception
    return user

otp_store = {}

def generate_otp(user_id, validity=300):

    otp = ''.join(random.choices(string.digits, k=6))
    expiry = time.time() + validity  
    otp_hash = sha256(otp.encode()).hexdigest()
    otp_store[user_id] = {"otp_hash": otp_hash, "expiry": expiry}
    
    return otp

def verify_otp(user_id, otp):

    if user_id not in otp_store:
        return False  
    stored_otp_data = otp_store[user_id]

    if time.time() > stored_otp_data["expiry"]:
        del otp_store[user_id]  
        return False

    otp_hash = sha256(otp.encode()).hexdigest()
    if otp_hash == stored_otp_data["otp_hash"]:
        del otp_store[user_id]  
        return True
    
    return False



