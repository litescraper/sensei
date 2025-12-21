"""
Tests for LLM provider module.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.llm_providers import LLMProvider, AVAILABLE_MODELS
from tests.conftest import mock_env_vars


class TestLLMProvider:
    """Test LLMProvider class."""
    
    def test_create_llm_google(self, mock_env_vars):
        """Test creating Google Gemini LLM."""
        llm = LLMProvider.create_llm("google", model_name="gemini-3-flash-preview")
        assert llm is not None
    
    def test_create_llm_anthropic(self, mock_env_vars):
        """Test creating Anthropic Claude LLM."""
        # Skip if not installed
        try:
            llm = LLMProvider.create_llm("anthropic", model_name="claude-3-5-sonnet-20241022")
            assert llm is not None
        except ImportError:
            pytest.skip("langchain-anthropic not installed")
    
    def test_create_llm_openai(self, mock_env_vars):
        """Test creating OpenAI LLM."""
        # Skip if API key not available
        try:
            llm = LLMProvider.create_llm("openai", model_name="gpt-4o")
            assert llm is not None
        except ValueError:
            pytest.skip("OPENAI_API_KEY not available")
    
    def test_create_llm_groq(self, mock_env_vars):
        """Test creating Groq LLM."""
        llm = LLMProvider.create_llm("groq", model_name="llama-3.3-70b-versatile")
        assert llm is not None
    
    def test_create_llm_invalid_provider(self, mock_env_vars):
        """Test creating LLM with invalid provider."""
        with pytest.raises(ValueError):
            LLMProvider.create_llm("invalid_provider")
    
    def test_available_models_structure(self):
        """Test that AVAILABLE_MODELS has correct structure."""
        assert isinstance(AVAILABLE_MODELS, dict)
        assert "google" in AVAILABLE_MODELS
        assert "groq" in AVAILABLE_MODELS
        
        # Check that each provider has models (can be dict or list)
        for provider, models in AVAILABLE_MODELS.items():
            assert isinstance(models, (dict, list))
            assert len(models) > 0
    
    def test_default_models_exist(self):
        """Test that default models are specified."""
        for provider, models in AVAILABLE_MODELS.items():
            # Check that at least one model exists
            assert len(models) > 0
            # Check structure - can be dict or list
            if isinstance(models, dict):
                for model_name in models.keys():
                    assert isinstance(model_name, str)
            elif isinstance(models, list):
                for model_name in models:
                    assert isinstance(model_name, str)

