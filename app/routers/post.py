from typing import List, Optional
from fastapi import Depends, HTTPException, status, APIRouter
from sqlmodel import select
import app.oauth2 as oauth2
from app.database import SessionDep
from app.models import Post, Vote
from app.schemas import PostCreateUpdate, PostSchema, PostOut
from sqlalchemy import func
from app.utils import sanitize_input

router = APIRouter(prefix="/posts", tags=["Post"])


@router.get("/", response_model=List[PostOut])
async def get_posts(
    db: SessionDep,
    limit: int = 10,
    offset: int = 0,
    search: Optional[str] = "",
    current_user=Depends(oauth2.get_current_user),
):

    query = db.exec(
        select(Post, func.count(Vote.post_id).label("votes"))
        .join(Vote, Vote.post_id == Post.id, isouter=True)
        .group_by(Post.id)
        .filter(Post.title.ilike(f"%{search}%"))
        .limit(limit)
        .offset(offset)
    )
    posts = query.mappings().all()
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostSchema)
async def create_post(
    post_data: PostCreateUpdate,
    db: SessionDep,
    current_user=Depends(oauth2.get_current_user),
):
    post_data.title = sanitize_input(post_data.title)
    post_data.content = sanitize_input(post_data.content)
    new_post = Post(owner_id=current_user.id, **post_data.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=PostOut)
async def get_post(
    id: int, db: SessionDep, current_user=Depends(oauth2.get_current_user)
):
    query = db.exec(
        select(Post, func.count(Vote.post_id).label("votes"))
        .join(Vote, Vote.post_id == Post.id, isouter=True)
        .where(Post.id == id)
        .group_by(Post.id)
    )
    post = query.mappings().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not exist",
        )
    return post


@router.put("/{id}", response_model=PostSchema)
async def update_post(
    id: int,
    post: PostCreateUpdate,
    db: SessionDep,
    current_user=Depends(oauth2.get_current_user),
):
    existing_post = db.get(Post, id)

    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )
    if existing_post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorised to perform requsted action",
        )
    if post.title:
        post.title = sanitize_input(post.title)
    if post.content:
        post.content = sanitize_input(post.content)
    post_data = post.model_dump(exclude_unset=True)
    existing_post.sqlmodel_update(post_data)
    db.add(existing_post)
    db.commit()
    db.refresh(existing_post)
    return existing_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id: int, db: SessionDep, current_user=Depends(oauth2.get_current_user)
):
    deleted_post = db.get(Post, id)

    if not deleted_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )
    if deleted_post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorised to perform requsted action",
        )

    db.delete(deleted_post)
    db.commit()
    return
