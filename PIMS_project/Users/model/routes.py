from Users.model.schemas import Users, PasswordResetRequest, resetpassword
from fastapi import APIRouter, HTTPException, Depends
from shared.database import get_db
from sqlalchemy.orm import Session
from shared.security import user_access
from Users.model.services import check_user_permission, validate_and_hash_password
from starlette import status
from shared.send_mail import send_email
from shared.security import generate_otp, verify_otp
from Users.model.models import Users


router = APIRouter(prefix='/user', tags=['users_auth'])

@router.post("/request/password/reset/mail")
async def request_password_reset(data: PasswordResetRequest,
                                 session: Session = Depends(get_db),
                                 current_user: Users = Depends(user_access)):

    check_user_permission(current_user, data.email)

    db_user = session.query(Users).filter(Users.email == data.email).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found.")

    otp = generate_otp(data.email)
    message = f"Your OTP for password reset is: {otp}. It will expire in 5 minutes."
    send_email("syedaghazalzehra89@gmail.com", data.email, "Password Reset OTP", message)

    return {"message": "Password reset OTP sent successfully."}

async def reset_password_page(token: str):
    return f"Your Password Reset Token: {token}\nUse this token in Postman to reset your password."

@router.post("/reset/password/")
def reset_password(user: resetpassword,  
                   session: Session = Depends(get_db), 
                   current_user: Users = Depends(user_access)):
    
    check_user_permission(current_user, user.email)

    if not verify_otp(user.email, user.otp):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="Invalid or expired OTP.")

    users = session.query(Users).filter(Users.email == user.email).first()

    hashed_password = validate_and_hash_password(user.new_password)

    users.password = hashed_password
    session.commit()

    return {"message": "Password reset successfully."}


@router.delete("/deleteusers/{user_id}")
def deleteuser(user_id:int,
               session: Session=Depends(get_db), 
               current_user: Users = Depends(user_access)):
   user = session.query(Users).get(user_id)
   
   if not user:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"User doesn't exists.")
   
   check_user_permission(current_user, user.email)
   
   if current_user.email != current_user.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are successfully removed..")
   
   session.delete(user)
   session.commit()
   session.close()
   return {f"User {user_id} was deleted."}



