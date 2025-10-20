"""Continuous simulation job (runs every 1 minute)."""
from dagster import ScheduleDefinition, job

from dagster.assets.interactions import simulated_interactions
from dagster.assets.posts import generated_posts


@job
def continuous_simulation():
    """Generate posts and interactions continuously."""
    generated_posts()
    simulated_interactions()


# Schedule: Every 1 minute
continuous_schedule = ScheduleDefinition(
    job=continuous_simulation,
    cron_schedule="*/1 * * * *",  # Every minute
    name="continuous_simulation_schedule",
)
