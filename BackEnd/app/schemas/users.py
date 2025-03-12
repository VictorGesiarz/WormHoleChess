
from pydantic import BaseModel
from typing import Optional, List, Dict


# Model to define the data required for user registration (POST /register)
class UserCreate(BaseModel):
    email: str
    password: str
    username: str

    class Config:
        # This ensures that Pydantic will treat incoming data as camelCase, e.g., 'firstName'
        alias_generator = lambda s: ''.join([word.capitalize() if i != 0 else word for i, word in enumerate(s.split('_'))])


# Model to return user data in response (GET /users/{id})
class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True  # This allows Pydantic to work with SQLAlchemy models (ORM)


class Token(BaseModel): 
    access_token: str
    token_type: str
