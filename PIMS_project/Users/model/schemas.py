from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class Roles(str, Enum):
    user = "user"
    admin = "admin"

class Users(BaseModel): 

    username : str
    password : str
    email : EmailStr
    role: Roles = "user"


class signup_user(BaseModel):

    username : str
    password : str
    email : EmailStr
    role: str = "user"


class login_user(BaseModel):

    username : Optional[str] = None
    password : str
    email : Optional[EmailStr] = None


class resetpassword(BaseModel):
    otp: str
    email: EmailStr
    new_password: str


class PasswordResetRequest(BaseModel):
    email: str









