from fastapi import APIRouter, HTTPException, Depends
from Users.model.models import Users
from Users.model.schemas import signup_user, login_user
from sqlalchemy.orm import Session
from shared.database import get_db
from Users.model.services import validate_and_hash_password
from shared.security import create_token
from starlette import status
from sqlalchemy import or_
from shared.send_mail import send_email



router = APIRouter(prefix='/auth', tags=['auth'])

@router.post("/signup")
def signup(user: signup_user, session: Session = Depends(get_db)):

    existing_user_by_username = session.query(Users).filter(Users.username == user.username).first()
    existing_user_by_email = session.query(Users).filter(Users.email == user.email).first()

    if existing_user_by_username:
        raise HTTPException(status_code=400, detail=f"Username '{user.username}' already exists.")
    if existing_user_by_email:
        raise HTTPException(status_code=400, detail=f"Email '{user.email}' already exists.")
    
    new_user = Users()
    new_user.username = user.username
    username = new_user.username

    if not any(char.isalpha() for char in user.username):
        raise HTTPException(
            status_code=400,
            detail="Username must contain at least one alphabet."
        )
    
    if user.username[0].isdigit():
        raise HTTPException(
            status_code=400,
            detail="Username must not start with a number."
        )

    hashed_password = validate_and_hash_password(user.password)

    new_user.password = hashed_password
    new_user.email = user.email
    new_user.role = user.role if user.role in ["admin", "user"] else "user"  # Assign role
    email = new_user.email

    message = f"""Dear {username},\n\nYou have been registered successfully."""
    send_email(email, email, "Registration Successful", message)

    session.add(new_user)
    session.commit()

    return {"message": "User registered successfully", "user": {"username": username, "email": email,  "role": new_user.role}}


@router.get("/login")
def login(user: login_user, session: Session = Depends(get_db)):

    db_user = session.query(Users).filter(
        or_(
            Users.username == user.username,
            Users.email == user.email
        )
    ).first()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Invalid username/email or password.")

    hashed_password = validate_and_hash_password(user.password)

    access_token = create_token(data={"sub": db_user.username,
                                      "email": db_user.email})

    return {
        "access token": access_token,
        "token_type": "bearer",
        "username": db_user.username,
        "email": db_user.email,
        "role": db_user.role
    }