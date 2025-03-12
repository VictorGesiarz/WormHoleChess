from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session

from databases import Database

# Replace these with your actual database credentials
DATABASE_URL = "postgresql://postgres:19732003@localhost/chess_game"

# Create a SQLAlchemy engine
engine = create_engine(DATABASE_URL) 

# SessionLocal is used to create and manage database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for all models
Base = declarative_base()

# Async Database connection setup
database = Database(DATABASE_URL)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]