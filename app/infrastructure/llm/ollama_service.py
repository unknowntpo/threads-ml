"""Ollama LLM service implementation."""
import os
from typing import Optional

from ollama import Client

from app.domain.services.llm_interface import LLMInterface


class OllamaService(LLMInterface):
    """Ollama-based LLM service using Gemma 3 270M."""

    def __init__(self, base_url: Optional[str] = None, model: str = "gemma3:270m"):
        """Initialize Ollama client.

        Args:
            base_url: Ollama server URL (defaults to env var or docker service)
            model: Model name to use
        """
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        self.model = model
        self.client = Client(host=self.base_url)

    def generate_post(self, interest: str) -> str:
        """Generate post content based on interest."""
        prompt = (
            f"Create a short social media post about {interest}. "
            f"Make it casual and engaging. Maximum 280 characters. "
            f"Do not use hashtags."
        )

        response = self.client.generate(model=self.model, prompt=prompt)
        content = response['response'].strip()

        # Truncate if too long
        if len(content) > 280:
            content = content[:277] + "..."

        return content

    def generate_comment(self, post_content: str, interest: str) -> str:
        """Generate comment for a post."""
        prompt = (
            f"You are a {interest} enthusiast. "
            f"Write a short, natural comment (1-2 sentences) on this post: \"{post_content}\". "
            f"Be friendly and relevant to the topic."
        )

        response = self.client.generate(model=self.model, prompt=prompt)
        return response['response'].strip()

    def should_interact(self, post_content: str, interest: str) -> bool:
        """Decide if user would interact with post."""
        prompt = (
            f"You are a {interest} enthusiast. "
            f"Would you be interested in this post: \"{post_content}\"? "
            f"Answer only 'yes' or 'no'."
        )

        response = self.client.generate(model=self.model, prompt=prompt)
        answer = response['response'].strip().lower()

        return 'yes' in answer

    def generate_display_name(self, interest: str) -> str:
        """Generate realistic display name."""
        prompt = (
            f"Create a short, catchy display name (1-2 words) "
            f"for a {interest} enthusiast. "
            f"Just return the name, nothing else."
        )

        response = self.client.generate(model=self.model, prompt=prompt)
        name = response['response'].strip()

        # Clean up any quotes or extra text
        name = name.replace('"', '').replace("'", '').split()[0]

        return name[:20]  # Limit length
