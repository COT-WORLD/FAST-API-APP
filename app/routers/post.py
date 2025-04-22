from typing import List, Optional
from fastapi import Depends, HTTPException, status, APIRouter
from sqlmodel import select
import oauth2
from database import SessionDep
from models import Post, Vote
from schemas import PostCreateUpdate, PostSchema, PostOut
from sqlalchemy import func

router = APIRouter(
    prefix="/posts", tags=["Post"]
)


@router.get("/", response_model=List[PostOut])
def get_posts(db: SessionDep, limit: int = 10, offset: int = 0, search: Optional[str] = ""):

    query = db.exec(select(Post, func.count(Vote.post_id).label("votes")).join(
        Vote, Vote.post_id == Post.id, isouter=True).group_by(Post.id).filter(Post.title.ilike(f"%{search}%")).limit(limit).offset(offset))
    posts = query.mappings().all()
    return posts


@router.post("/",  status_code=status.HTTP_201_CREATED, response_model=PostSchema)
def create_post(post_data: PostCreateUpdate, db: SessionDep, current_user=Depends(oauth2.get_current_user)):
    new_post = Post(owner_id=current_user.id, **post_data.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=PostOut)
def get_post(id: int, db: SessionDep, current_user=Depends(oauth2.get_current_user)):
    query = db.exec(select(Post, func.count(Vote.post_id).label("votes")).join(
        Vote, Vote.post_id == Post.id, isouter=True).where(Post.id == id).group_by(Post.id))
    post = query.mappings().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} doesn't exist")
    return post


@router.put("/{id}", response_model=PostSchema)
def update_post(id: int, post: PostCreateUpdate, db: SessionDep, current_user=Depends(oauth2.get_current_user)):

    existing_post = db.get(Post, id)

    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} doesn't found")
    if existing_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not authorised to perform requsted action")

    hero_data = post.model_dump(exclude_unset=True)
    existing_post.sqlmodel_update(hero_data)
    db.add(existing_post)
    db.commit()
    db.refresh(existing_post)
    return existing_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: SessionDep, current_user=Depends(oauth2.get_current_user)):
    deleted_post = db.get(Post, id)

    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} doesn't found")
    if deleted_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not authorised to perform requsted action")

    db.delete(deleted_post)
    db.commit()
    return deleted_post
