"""Dagster asset for generating posts from fake users."""
import random
import uuid
from datetime import datetime

from dagster import asset

from app.infrastructure.database.models import Post
from app.infrastructure.database.queries import extract_interest_from_bio, get_fake_users


@asset(deps=["fake_users"])
def generated_posts(db, ollama):
    """Generate 1-3 posts from random fake users.

    Uses Ollama to create interest-based content.
    """
    session = db()

    fake_user_list = get_fake_users(session)
    if not fake_user_list:
        session.close()
        return {"status": "no_fake_users", "posts_created": 0}

    # Generate 1-3 posts
    posts_to_create = random.randint(1, 3)
    posts_created = 0

    for _ in range(posts_to_create):
        user = random.choice(fake_user_list)
        interest = extract_interest_from_bio(user.bio)

        if not interest:
            continue

        try:
            content = ollama.generate_post(interest)

            post = Post(
                id=str(uuid.uuid4()),
                user_id=user.id,
                content=content,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            session.add(post)
            posts_created += 1
        except Exception as e:
            # Log error but continue
            print(f"Error generating post: {e}")
            continue

    session.commit()
    session.close()

    return {"status": "success", "posts_created": posts_created}
