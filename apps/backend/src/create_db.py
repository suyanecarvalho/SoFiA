from database.connection import engine
from database.models import Base

def init_db():
    """
    Creates all database tables defined in models.py.
    """
    print("Connecting to the database and creating tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    init_db()