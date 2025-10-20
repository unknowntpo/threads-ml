"""Dagster asset for simulating user interactions."""
import random
import uuid
from datetime import datetime

from dagster import asset

from app.infrastructure.database.models import UserInteraction
from app.infrastructure.database.queries import (
    extract_interest_from_bio,
    get_fake_users,
    get_recent_posts,
)


@asset(deps=["fake_users", "generated_posts"], required_resource_keys={"db", "ollama"})
def simulated_interactions(context):
    """Simulate likes, comments, and views from fake users.

    Users interact with posts based on interest matching.
    """
    db = context.resources.db
    ollama = context.resources.ollama
    session = db()

    fake_user_list = get_fake_users(session)
    recent_posts_list = get_recent_posts(session, hours=24)

    if not fake_user_list or not recent_posts_list:
        session.close()
        return {"status": "no_data", "interactions": 0}

    interactions_created = 0

    # Each fake user evaluates recent posts
    for user in fake_user_list:
        interest = extract_interest_from_bio(user.bio)
        if not interest:
            continue

        # Sample up to 5 random posts
        sample_posts = random.sample(recent_posts_list, min(5, len(recent_posts_list)))

        for post in sample_posts:
            # Skip own posts
            if post.user_id == user.id:
                continue

            try:
                # Check if user would interact
                would_interact = ollama.should_interact(post.content, interest)

                if would_interact:
                    # Weighted random action
                    action = random.choices(
                        ['view', 'like', 'comment'], weights=[0.5, 0.3, 0.2]
                    )[0]

                    if action == 'view':
                        # Create view interaction
                        interaction = UserInteraction(
                            id=str(uuid.uuid4()),
                            user_id=user.id,
                            post_id=post.id,
                            interaction_type='view',
                            interaction_metadata={'duration_seconds': random.randint(5, 60)},
                            created_at=datetime.utcnow(),
                        )
                        session.add(interaction)
                        interactions_created += 1

                    elif action == 'like':
                        # Check if already liked (check UserInteraction for existing like)
                        existing_like = (
                            session.query(UserInteraction)
                            .filter_by(user_id=user.id, post_id=post.id, interaction_type='like')
                            .first()
                        )

                        if not existing_like:
                            # Create interaction record for like
                            interaction = UserInteraction(
                                id=str(uuid.uuid4()),
                                user_id=user.id,
                                post_id=post.id,
                                interaction_type='like',
                                created_at=datetime.utcnow(),
                            )
                            session.add(interaction)
                            interactions_created += 1

                    # TODO: Implement comment generation

            except Exception as e:
                print(f"Error creating interaction: {e}")
                continue

    session.commit()
    session.close()

    return {"status": "success", "interactions": interactions_created}
