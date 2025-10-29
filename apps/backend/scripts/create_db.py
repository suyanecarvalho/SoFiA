import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from apps.backend.src.db.database.base import Base
from apps.backend.src.db.database.connection import engine

# noinspection PyUnusedImports


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
