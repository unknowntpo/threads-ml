"""Top-level Dagster definitions for ML service."""
import os

from dagster import Definitions, load_assets_from_package_module

from threads_ml.simulation import assets, jobs, resources

# Load all simulation assets
simulation_assets = load_assets_from_package_module(assets)

# Define simulation resources
simulation_resources = {
    "db": resources.DBResource(),
    "ollama": resources.OllamaResource(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://ollama:11434"),
        model="gemma3:270m",
    ),
}

# Create combined definitions
defs = Definitions(
    assets=simulation_assets,
    jobs=[jobs.continuous_simulation, jobs.manual_simulation],
    schedules=[jobs.continuous_schedule],
    resources=simulation_resources,
)
