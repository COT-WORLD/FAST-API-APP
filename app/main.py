from fastapi import FastAPI
from database import create_db_and_tables
from contextlib import asynccontextmanager
from routers import post, user


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(user.router)
app.include_router(post.router)


@app.get("/")
def read_root():
    return {"Hello World"}
