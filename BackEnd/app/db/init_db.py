from db.database import engine, Base
from models.users import User 

def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")
