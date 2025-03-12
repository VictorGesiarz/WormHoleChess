from sqlalchemy.orm import Session
from sqlalchemy.sql import text  # Import text() to wrap raw SQL
from db.database import SessionLocal  # Adjust based on your structure

def test_connection():
    try:
        db: Session = SessionLocal()
        db.execute(text("SELECT 1"))  # Wrap query in text()
        print("✅ Successfully connected to the database!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    finally:
        db.close()

# test_connection()


from sqlalchemy import inspect
from db.database import engine  # Import your database engine

inspector = inspect(engine)
tables = inspector.get_table_names()

print("📋 Tables in database:", tables)


from db.init_db import init_db
# init_db()