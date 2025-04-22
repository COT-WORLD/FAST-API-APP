from datetime import datetime
from pydantic import BaseModel, EmailStr
from sqlmodel import SQLModel, Field
from pydantic import model_validator
from typing import Optional


class UserBase(SQLModel):
    email: EmailStr
    password: str


class UserSchema(SQLModel):
    id: int
    email: EmailStr


class PostCreateUpdate(SQLModel):
    title: str
    content: str
    published: bool = True


class PostSchema(SQLModel):
    id: int
    title: str
    content: str
    published: bool = True
    created_at: datetime
    owner_id: int
    owner: UserSchema

    model_config = {
        "from_attributes": True
    }


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None


class VoteSchema(SQLModel):
    post_id: int
    dir: int = Field(default=0)

    @model_validator(mode="before")
    def check_dir(cls, values):
        dir_value = values.get("dir")
        if dir_value not in (0, 1):
            raise ValueError("dir must be 0 or 1")
        return values


class PostOut(SQLModel):
    Post: PostSchema
    votes: int

    model_config = {
        "from_attributes": True
    }
