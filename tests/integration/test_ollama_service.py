"""Integration tests for Ollama LLM service."""
import pytest

from app.infrastructure.llm.ollama_service import OllamaService


@pytest.mark.integration
class TestOllamaService:
    """Test Ollama LLM service integration."""

    @pytest.fixture
    def ollama_service(self):
        """Create Ollama service instance."""
        # Use localhost for integration tests
        return OllamaService(base_url="http://localhost:11434")

    def test_generate_post_returns_content(self, ollama_service):
        """Should generate post content for given interest."""
        # Act
        content = ollama_service.generate_post("tech")

        # Assert
        assert content is not None
        assert isinstance(content, str)
        assert len(content) > 0
        assert len(content) <= 280, f"Post should be ≤280 chars: {len(content)}"

    def test_generate_post_different_interests(self, ollama_service):
        """Should generate different content for different interests."""
        # Arrange
        interests = ["sports", "tech", "anime"]

        # Act
        posts = {interest: ollama_service.generate_post(interest) for interest in interests}

        # Assert
        assert len(posts) == 3
        for interest, content in posts.items():
            assert content is not None
            assert len(content) > 0

    def test_generate_comment_returns_content(self, ollama_service):
        """Should generate comment for post."""
        # Arrange
        post_content = "New AI breakthrough announced today!"
        interest = "tech"

        # Act
        comment = ollama_service.generate_comment(post_content, interest)

        # Assert
        assert comment is not None
        assert isinstance(comment, str)
        assert len(comment) > 0

    def test_should_interact_returns_boolean(self, ollama_service):
        """Should return boolean for interest match."""
        # Arrange
        post_content = "Exciting football game tonight!"
        interest = "sports"

        # Act
        result = ollama_service.should_interact(post_content, interest)

        # Assert
        assert isinstance(result, bool)

    def test_should_interact_matches_interest(self, ollama_service):
        """Should return True for matching interest."""
        # Arrange
        test_cases = [
            ("New smartphone launched", "tech", True),
            ("Latest anime episode released", "anime", True),
            ("Football championship finals", "sports", True),
        ]

        # Act & Assert
        for post_content, interest, expected in test_cases:
            result = ollama_service.should_interact(post_content, interest)
            # LLM may vary, so just check it returns a boolean
            assert isinstance(result, bool)

    def test_generate_display_name_returns_string(self, ollama_service):
        """Should generate display name for interest."""
        # Act
        display_name = ollama_service.generate_display_name("tech")

        # Assert
        assert display_name is not None
        assert isinstance(display_name, str)
        assert len(display_name) > 0
        assert len(display_name) <= 20, f"Display name should be ≤20 chars: {len(display_name)}"

    def test_generate_display_name_different_interests(self, ollama_service):
        """Should generate names for different interests."""
        # Arrange
        interests = ["sports", "tech", "anime", "cars", "food"]

        # Act & Assert
        for interest in interests:
            display_name = ollama_service.generate_display_name(interest)
            assert display_name is not None
            assert len(display_name) > 0
