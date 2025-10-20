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

    context.log.info(f"Interaction simulation: {len(fake_user_list)} fake users, {len(recent_posts_list)} recent posts")

    if not fake_user_list or not recent_posts_list:
        context.log.warning(f"Insufficient data: fake_users={len(fake_user_list)}, recent_posts={len(recent_posts_list)}")
        session.close()
        return {"status": "no_data", "interactions": 0}

    interactions_created = 0
    interactions_by_type = {"view": 0, "like": 0, "comment": 0}

    # Each fake user evaluates recent posts
    for user in fake_user_list:
        interest = extract_interest_from_bio(user.bio)
        if not interest:
            context.log.debug(f"No interest found for user {user.username}, skipping")
            continue

        # Sample up to 5 random posts
        sample_posts = random.sample(recent_posts_list, min(5, len(recent_posts_list)))
        context.log.info(f"User {user.username} (interest={interest}) evaluating {len(sample_posts)} posts")

        posts_evaluated = 0
        for post in sample_posts:
            # Skip own posts
            if post.user_id == user.id:
                context.log.debug(f"Skipping own post {post.id[:8]}...")
                continue

            posts_evaluated += 1

            try:
                # Check if user would interact
                context.log.debug(f"Asking Ollama if user interested in: {post.content[:50]}...")
                would_interact = ollama.should_interact(post.content, interest)
                context.log.debug(f"Ollama response: would_interact={would_interact}")

                if would_interact:
                    # Weighted random action
                    action = random.choices(
                        ['view', 'like', 'comment'], weights=[0.5, 0.3, 0.2]
                    )[0]

                    context.log.info(f"User {user.username} will '{action}' post {post.id[:8]}...")

                    if action == 'view':
                        # Create view interaction
                        duration = random.randint(5, 60)
                        interaction = UserInteraction(
                            id=str(uuid.uuid4()),
                            user_id=user.id,
                            post_id=post.id,
                            interaction_type='view',
                            interaction_metadata={'duration_seconds': duration},
                            created_at=datetime.utcnow(),
                        )
                        session.add(interaction)
                        interactions_created += 1
                        interactions_by_type['view'] += 1
                        context.log.info(f"Created VIEW (duration={duration}s)")

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
                            interactions_by_type['like'] += 1
                            context.log.info(f"Created LIKE")
                        else:
                            context.log.debug(f"Already liked, skipping")

                    elif action == 'comment':
                        context.log.debug(f"Comment generation not yet implemented")
                        # TODO: Implement comment generation

            except Exception as e:
                context.log.error(f"Error creating interaction: {e}")
                continue

        context.log.info(f"User {user.username} evaluated {posts_evaluated} posts")

    session.commit()
    context.log.info(f"Interaction simulation complete: {interactions_created} total (views={interactions_by_type['view']}, likes={interactions_by_type['like']}, comments={interactions_by_type['comment']})")
    session.close()

    return {"status": "success", "interactions": interactions_created}
