import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

current_file_path = Path(__file__).resolve()
BACKEND_ROOT = current_file_path.parents[3]
DATA_DIR = BACKEND_ROOT / "data"
DATABASE_PATH = DATA_DIR / "sofia.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
os.makedirs(DATA_DIR, exist_ok=True)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
