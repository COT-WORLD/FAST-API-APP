from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    test_database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"


settings = Settings()

postgres_url = settings.database_url

engine = create_engine(postgres_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
