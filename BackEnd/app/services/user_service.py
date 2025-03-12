from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

from db.database import db_dependency
from models.users import User
from schemas.users import UserCreate, UserResponse
import config


# For hashing passwords
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)

# Function to hash the password
def hash_password(password: str) -> str:
    return bcrypt_context.hash(password)

# Function to check the password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)

# Function to create a new user
def create_user(db: Session, user_create: UserCreate) -> User:
    hashed_password = hash_password(user_create.password)
    db_user = User(username=user_create.username, email=user_create.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Function to authenticate a user by email and password
def authenticate_user_via_email(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if user and verify_password(password, user.password):
        return user
    return None


def authenticate_user_via_username(db: Session, username: str, password: str) -> User:
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.password):
        return user
    return None


def create_access_token(username: str, user_id: int, expires_delta: timedelta) -> str:
    encode = {"sub": username, "user_id": user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, config.SECRET_KEY, config.ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: db_dependency):
    
    try: 
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username: str = payload.get("sub")  # Now extracting email instead of username
        user_id: int = payload.get("user_id")

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        return UserResponse(id=user.id, username=user.username, email=user.email)

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    

user_dependency = Annotated[dict, Depends(get_current_user)]