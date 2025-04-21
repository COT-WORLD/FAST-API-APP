from datetime import datetime
from pydantic import EmailStr
from sqlmodel import SQLModel


class PostBase(SQLModel):
    title: str
    content: str
    published: bool = True


class PostCreateUpdate(PostBase):
    pass


class PostSchema(PostBase):
    id: int
    created_at: datetime


class UserBase(SQLModel):
    email: EmailStr
    password: str


class UserSchema(SQLModel):
    id: int
    email: EmailStr
