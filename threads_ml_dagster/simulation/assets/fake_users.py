"""Dagster asset for managing fake users."""
from dagster import asset

from app.domain.factories.fake_user_factory import FakeUserFactory
from app.infrastructure.database.queries import count_fake_users


@asset
def fake_users(db, ollama):
    """Ensure 5-10 fake users exist in database.

    Creates users with different interests if count is below target.
    """
    session = db()

    existing_count = count_fake_users(session)
    target_count = 8

    if existing_count >= target_count:
        session.close()
        return {"status": "sufficient", "count": existing_count}

    # Create missing users
    factory = FakeUserFactory()
    created = 0

    for interest in FakeUserFactory.INTERESTS:
        if existing_count + created >= target_count:
            break

        user = factory.create_fake_user(interest, ollama, activity_level=0.7)
        session.add(user)
        created += 1

    session.commit()
    final_count = count_fake_users(session)
    session.close()

    return {"status": "created", "count": final_count, "created": created}
