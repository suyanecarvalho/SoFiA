from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session

from src.db.crud import crud_user
from src.db.schemas import user as user_schema
from src.db.database.connection import get_db

router = APIRouter()


@router.post(
    "",
    response_model=user_schema.User,
    status_code=status.HTTP_201_CREATED,
    summary="Create the primary user",
)
def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.

    **Constraints**:
    - This system allows **only one user**.
    - If a user already exists, this endpoint will return a 400 error.
    """
    existing_user = crud_user.get_existing_user(db)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user already exists. This system is limited to a single user.",
        )
    return crud_user.create_user(db=db, user=user)


@router.put(
    "/{user_id}",
    response_model=user_schema.User,
    status_code=status.HTTP_200_OK,
    summary="Update user details",
)
def update_user(
    user_update: user_schema.UserUpdate,
    user_id: int = Path(..., description="The ID of the user to update"),
    db: Session = Depends(get_db),
):
    """
    Update the user's name, profile picture, or API key.
    Only updates the fields provided in the payload.
    """
    db_user = crud_user.update_user(db=db, user_id=user_id, user_update=user_update)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )

    return db_user
