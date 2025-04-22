from fastapi import Depends, HTTPException, status, APIRouter
from sqlmodel import select

from app.models import User
from app.schemas import Token
from app.database import SessionDep
from app.utils import verify_password
from app.oauth2 import create_access_token
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login(db: SessionDep, user_credentials: OAuth2PasswordRequestForm = Depends()):
    user = db.exec(select(User).filter(
        User.email == user_credentials.username)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials!")
    if not verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials!")
    access_token = create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}
