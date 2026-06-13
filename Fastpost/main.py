from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import Fastpost.auth as auth
from Fastpost.database import create_db_and_tables
from Fastpost.routers import post, user, vote


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(post.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/")
def read_root():
    return {
        "message": "Hello World successfully deployed on Render via CICD pipeline(Github Actions)"
    }
