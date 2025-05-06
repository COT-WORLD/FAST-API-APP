from typing import List
from fastapi import Depends, HTTPException, status, APIRouter
from sqlmodel import select
from app.schemas import VoteSchema
from app.models import Post, Vote
from app.database import SessionDep
import app.oauth2 as oauth2


router = APIRouter(
    prefix="/vote",
    tags=["Vote"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_votes(vote: VoteSchema, db: SessionDep, current_user=Depends(oauth2.get_current_user)):

    post = db.exec(select(Post).filter(Post.id == vote.post_id)).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {vote.post_id} doesn't exist")
    already_voted = db.exec(select(Vote).filter(
        Vote.post_id == vote.post_id, Vote.user_id == current_user.id)).first()
    if vote.dir == 1:
        if already_voted:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"user {current_user.id} has already voted on post {vote.post_id}")
        new_vote = Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "Successfully added vote"}
    else:
        if not already_voted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Vote not found")
        db.delete(already_voted)
        db.commit()
        return {"message": "Successfully deleted vote"}
