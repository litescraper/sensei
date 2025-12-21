import pytest
import os
from unittest.mock import patch


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test_google_key")
    monkeypatch.setenv("GROQ_API_KEY", "test_groq_key")
    monkeypatch.setenv("SERPAPI_API_KEY", "test_serpapi_key")
    monkeypatch.setenv("SEMANTICSCHOLAR_API_KEY", "test_s2_key")


@pytest.fixture
def sample_paper():
    """Fixture for a sample Paper object."""
    from datetime import datetime, timezone
    from src.models import Paper
    
    return Paper(
        title="Test Paper on AI Safety",
        abstract="This is a test abstract about AI safety research.",
        pdf_url="https://arxiv.org/pdf/1234.5678.pdf",
        published_date=datetime(2024, 6, 1, tzinfo=timezone.utc),
        arxiv_id="1234.5678",
        authors=["Author One", "Author Two"],
        categories=["cs.LG", "cs.CR"]
    )


@pytest.fixture
def sample_research_idea():
    """Fixture for a sample ResearchIdea object."""
    from src.models import ResearchIdea
    
    return ResearchIdea(
        title="Novel Approach to LLM Safety",
        abstract="A novel approach to ensuring LLM safety through adversarial training.",
        introduction="LLMs are increasingly powerful but face safety challenges...",
        method="We propose a new adversarial training method that...",
        expected_results="We expect to achieve 95% safety score...",
        keywords=["LLM", "Safety", "Adversarial Training", "AI"]
    )

