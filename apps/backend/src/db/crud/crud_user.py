import datetime
from sqlalchemy.orm import Session
from ..models import models
from ..schemas import user as user_schema


def get_user(db: Session, user_id: int) -> models.User | None:
    """
    Retrieve a single user by their ID.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_existing_user(db: Session) -> models.User | None:
    """
    Check if ANY user exists in the system.
    """
    return db.query(models.User).first()


def create_user(db: Session, user: user_schema.UserCreate) -> models.User:
    """
    Create a new user.
    Explicitly sets updated_at to now().
    """
    now = datetime.datetime.now()
    db_user = models.User(
        name=user.name,
        profile_pic=user.profile_pic,
        api_key=user.api_key,
        salary=user.salary,
        payday=user.payday,
        updated_at=now,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(
    db: Session, user_id: int, user_update: user_schema.UserUpdate
) -> models.User | None:
    """
    Update an existing user.
    Updates updated_at to now().
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    db_user.updated_at = datetime.datetime.now()
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
