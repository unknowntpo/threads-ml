"""Manual simulation job (triggered on-demand)."""
from dagster import job

from dagster.assets.fake_users import fake_users
from dagster.assets.interactions import simulated_interactions
from dagster.assets.posts import generated_posts


@job
def manual_simulation():
    """Full simulation pipeline - run on demand.

    Creates fake users, generates posts, and simulates interactions.
    """
    fake_users()
    generated_posts()
    simulated_interactions()
