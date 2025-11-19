from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session

from src.db.crud import crud_user
from src.db.schemas import user as user_schema
from src.db.database.connection import get_db
from src.utils.constants import APPLICATION_USER_ID  # <--- Imported constant

router = APIRouter()


@router.get(
    "/me",
    response_model=user_schema.User,
    status_code=status.HTTP_200_OK,
    summary="Get the primary user details",
)
def get_user(db: Session = Depends(get_db)):
    """
    Retrieve the details of the primary application user (ID defined in constants).
    """
    db_user = crud_user.get_user(db, user_id=APPLICATION_USER_ID)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Primary user not found. Please create the user first.",
        )

    return db_user


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
        db: Session = Depends(get_db),
):
    """
    Update the user's name, profile picture, or API key.
    Only updates the fields provided in the payload.
    """
    db_user = crud_user.update_user(db=db, user_id=APPLICATION_USER_ID, user_update=user_update)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {APPLICATION_USER_ID} not found.",
        )

    return db_user