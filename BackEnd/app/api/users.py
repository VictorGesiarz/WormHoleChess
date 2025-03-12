from fastapi import APIRouter, HTTPException, status
from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta


from schemas.users import UserCreate, UserResponse, Token
from models.users import User
from services.user_service import create_user, authenticate_user_via_email, authenticate_user_via_username, create_access_token,  user_dependency
from db.database import db_dependency


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/verify_token", status_code=status.HTTP_200_OK)
async def verify_token(user: user_dependency):
    if user is None: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    return {'User': 'Authenticated'}


@router.post("/user", response_model=UserResponse)
async def register_user(user_create: UserCreate, db: db_dependency): 
    # Check if the email or username already exists
    existing_user = db.query(User).filter((User.email == user_create.email) | (User.username == user_create.username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email or Username already registered")

    # Create the user
    new_user = create_user(db, user_create)
    return new_user


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency): 
    # Check if the input is an email or a username
    
    user = authenticate_user_via_email(db, form_data.username, form_data.password)
    if not user:
        user = authenticate_user_via_username(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create token using username
    token = create_access_token(user.username, user.id, timedelta(minutes=60 * 24))
    return {"access_token": token, "token_type": "bearer"}


@router.get("/get_email")
async def get_email(user: user_dependency):
    return {"email": user.email}