from typing import List
from fastapi import HTTPException, status, APIRouter
from sqlmodel import select
from app.database import SessionDep
from app.models import User
from app.schemas import UserBase, UserSchema
from app.utils import get_password_hash
from app.utils import sanitize_input

router = APIRouter(
    prefix="/users", tags=["User"]
)


@router.get("/", response_model=List[UserSchema])
async def get_users(db: SessionDep):
    users = db.exec(select(User)).all()
    return users


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserSchema)
async def create_user(user: UserBase, db: SessionDep):
    user.email = sanitize_input(user.email)
    user_exist = db.exec(select(User).filter(User.email == user.email)).first()
    if user_exist:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"User with email '{user.email}' already exists. Please use a different email or log in.")
    hashed_password = get_password_hash(user.password)
    user.password = hashed_password
    new_user = User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/{id}", response_model=UserSchema)
async def get_user(id: int, db: SessionDep):
    user = db.get(User, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} was not found")
    return user
