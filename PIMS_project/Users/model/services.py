from fastapi import HTTPException
from starlette import status
from shared.security import bcrypt_context

def check_user_permission(current_user, data_email):
    if current_user.role != "admin" and current_user.email != data_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access someone else's account."
        )
    
def validate_and_hash_password(password: str, is_new_password: bool = False):
    if not isinstance(password, str):
        raise HTTPException(status_code=400, detail="Password must be a string")

    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

    try:
        hashed_password = bcrypt_context.hash(password)
    except TypeError:
        raise HTTPException(status_code=400, detail="Invalid password format")

    if is_new_password:
        pass

    return hashed_password