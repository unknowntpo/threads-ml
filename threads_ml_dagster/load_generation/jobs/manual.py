"""Manual load generation job (triggered on-demand)."""
from dagster import job

from threads_ml_dagster.load_generation.assets.fake_users import fake_users
from threads_ml_dagster.load_generation.assets.interactions import (
    simulated_interactions,
)
from threads_ml_dagster.load_generation.assets.posts import generated_posts


@job
def manual_simulation():
    """Full simulation pipeline - run on demand.

    Creates fake users, generates posts, and simulates interactions.
    """
    users = fake_users()
    posts = generated_posts(users)
    simulated_interactions(posts)
