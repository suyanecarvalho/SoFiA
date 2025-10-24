import json
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Dict, Any

from apps.backend.src.db.database.base import Base
from apps.backend.src.db.models import models

def create_in_memory_db_session():
    """Creates a fresh, in-memory SQLite database and returns a session factory."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_base_data(db: Session, base_data_dir: str):
    """
    Seeds the database with foundational data from JSON files.
    Safely handles empty files.
    """
    files_to_load = {
        "categories": models.Category,
        "transactions": models.Transaction
    }
    for filename, model in files_to_load.items():
        file_path = os.path.join(base_data_dir, f"{filename}.json")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                content = f.read()
                if content.strip():
                    data = json.loads(content)
                    for item_data in data:
                        db.add(model(**item_data))

    db.commit()
def setup_test_case_state(db: Session, setup_data: Dict[str, Any]):
    """Adds test-case specific data to the database."""
    if 'transactions' in setup_data:
        for transaction_data in setup_data['transactions']:
            db.add(models.Transaction(**transaction_data))
    db.commit()