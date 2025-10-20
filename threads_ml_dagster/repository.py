"""Main Dagster repository definition."""
import os

from dagster import Definitions, load_assets_from_modules

from dagster.assets import fake_users, interactions, posts
from dagster.jobs.continuous import continuous_schedule, continuous_simulation
from dagster.jobs.manual import manual_simulation
from dagster.resources.db import DBResource
from dagster.resources.ollama import OllamaResource

# Load all assets
all_assets = load_assets_from_modules([fake_users, posts, interactions])

# Define resources
resources = {
    "db": DBResource(),
    "ollama": OllamaResource(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://ollama:11434"),
        model="gemma3:270m",
    ),
}

# Create Dagster definitions
defs = Definitions(
    assets=all_assets,
    jobs=[continuous_simulation, manual_simulation],
    schedules=[continuous_schedule],
    resources=resources,
)
