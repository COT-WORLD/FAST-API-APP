from typing import List
from fastapi import HTTPException, status, APIRouter
from sqlmodel import select
from database import SessionDep
from models import User
from schemas import UserBase, UserSchema
from utils import get_password_hash

router = APIRouter(
    prefix="/users", tags=["User"]
)


@router.get("/", response_model=List[UserSchema])
def get_users(db: SessionDep):
    users = db.exec(select(User)).all()
    return users


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserSchema)
def create_user(user: UserBase, db: SessionDep):
    user_exist = db.exec(select(User).filter(User.email == user.email)).first()
    if user_exist:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"User with email: {user.email} is exist, use diffrent email or login with this email")
    hashed_password = get_password_hash(user.password)
    user.password = hashed_password
    new_user = User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/{id}", response_model=UserSchema)
def get_user(id: int, db: SessionDep):
    user = db.get(User, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} doesn't found")
    return user
