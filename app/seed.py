from sqlmodel import Session, select
from models import User, Post, Vote
from utils import get_password_hash
from faker import Faker
from sqlalchemy.exc import IntegrityError
from database import engine  # your SQLModel engine setup
import random

fake = Faker()

USER_NAMES = [
    "Alice", "Bob", "Charlie", "Diana", "Ethan", "Fiona", "George", "Hannah", "Ivan", "Jasmine"
]

NUM_POSTS_PER_USER = 3
NUM_VOTES = 20


def seed_users(session: Session):
    users = []
    for name in USER_NAMES:
        email = f"{name.lower()}@gmail.com"
        existing_user = session.exec(
            select(User).where(User.email == email)).first()
        if existing_user:
            continue
        hashed_password = get_password_hash("password123")
        user = User(
            email=email,
            password=hashed_password  # You might want to hash in real apps
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        users.append(user)

    return users


def seed_posts(session: Session, users):
    posts = []
    for user in users:
        for _ in range(NUM_POSTS_PER_USER):
            post = Post(
                title=fake.sentence(nb_words=6),
                content=fake.paragraph(nb_sentences=3),
                owner_id=user.id,
                published=random.choice([True, False])
            )
            session.add(post)
            session.commit()
            session.refresh(post)
            posts.append(post)
    return posts


def seed_votes(session: Session, users, posts):
    for _ in range(NUM_VOTES):
        user = random.choice(users)
        post = random.choice(posts)

        # Avoid duplicate votes
        existing_vote = session.exec(
            select(Vote).where(Vote.user_id ==
                               user.id, Vote.post_id == post.id)
        ).first()

        if not existing_vote:
            vote = Vote(user_id=user.id, post_id=post.id)
            session.add(vote)

    session.commit()


def main():
    with Session(engine) as session:
        print("🌱 Seeding users...")
        users = seed_users(session)

        print("📝 Seeding posts...")
        posts = seed_posts(session, users)

        print("👍 Seeding votes...")
        seed_votes(session, users, posts)

        print("✅ Seeding completed.")


if __name__ == "__main__":
    main()
