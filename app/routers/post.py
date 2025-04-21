from typing import List
from fastapi import HTTPException, status, APIRouter
from sqlmodel import select
from database import SessionDep
from models import Post
from schemas import PostCreateUpdate, PostSchema

router = APIRouter(
    prefix="/posts", tags=["Post"]
)


@router.get("/", response_model=List[PostSchema])
def get_posts(db: SessionDep):
    posts = db.exec(select(Post)).all()
    return posts


@router.post("/",  status_code=status.HTTP_201_CREATED, response_model=PostSchema)
def create_post(post_data: PostCreateUpdate, db: SessionDep):
    new_post = Post(**post_data.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=PostSchema)
def get_post(id: int, db: SessionDep):
    post = db.get(Post, id)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} doesn't found")
    return post


@router.put("/{id}", response_model=PostSchema)
def update_post(id: int, post: PostCreateUpdate, db: SessionDep):
    existing_post = db.get(Post, id)
    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} doesn't found")
    hero_data = post.model_dump(exclude_unset=True)
    existing_post.sqlmodel_update(hero_data)
    db.add(existing_post)
    db.commit()
    db.refresh(existing_post)
    return existing_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: SessionDep):
    deleted_post = db.get(Post, id)

    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} doesn't found")
    db.delete(deleted_post)
    db.commit()
    return deleted_post
