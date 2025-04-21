from typing import Optional
from pydantic import EmailStr
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import Boolean, DateTime, text
from datetime import datetime


class Post(SQLModel, table=True):
    __tablename__ = "posts"
    id: int = Field(nullable=False, primary_key=True)
    title: str = Field(nullable=False)
    content: str = Field(nullable=False)
    published: Optional[bool] = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default="true")
    )
    created_at: datetime = Field(
        default_factory=datetime.now,  # Python-side default
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP")  # PostgreSQL-side default
        )
    )


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(nullable=False, primary_key=True)
    email: EmailStr = Field(nullable=False, unique=True)
    password: str = Field(nullable=False)
    created_at: datetime = Field(
        default_factory=datetime.now,  # Python-side default
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP")  # PostgreSQL-side default
        )
    )
