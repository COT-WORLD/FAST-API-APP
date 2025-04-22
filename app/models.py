from typing import List, Optional
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy import Boolean, DateTime, String, text, Integer, ForeignKey
from datetime import datetime


class Post(SQLModel, table=True):
    __tablename__ = "posts"
    id: int = Field(nullable=False, primary_key=True)
    title: str = Field(sa_column=Column(String, nullable=False))
    content: str = Field(sa_column=Column(String, nullable=False))
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
    owner_id: int = Field(
        nullable=False, foreign_key="users.id", ondelete="CASCADE")

    owner: Optional["User"] = Relationship(back_populates="posts")


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(nullable=False, primary_key=True)
    email: EmailStr = Field(sa_column=Column(
        String, nullable=False, unique=True))
    password: str = Field(sa_column=Column(String, nullable=False))
    created_at: datetime = Field(
        default_factory=datetime.now,  # Python-side default
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP")  # PostgreSQL-side default
        )
    )

    posts: List["Post"] = Relationship(back_populates="owner")


class Vote(SQLModel, table=True):
    __tablename__ = "votes"
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey(
            "users.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    )
    post_id: int = Field(
        sa_column=Column(Integer, ForeignKey(
            "posts.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    )
