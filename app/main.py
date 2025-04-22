from fastapi import FastAPI
from database import create_db_and_tables
from contextlib import asynccontextmanager
from routers import post, user, vote
import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(user.router)
app.include_router(post.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/")
def read_root():
    return {"Hello World"}
