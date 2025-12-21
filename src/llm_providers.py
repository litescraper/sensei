"""
Multi-provider LLM support for various AI models and inference providers.
"""
import os
from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel
import logging

logger = logging.getLogger(__name__)

# Optional imports for different providers
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

try:
    from langchain_anthropic import ChatAnthropic
except ImportError:
    ChatAnthropic = None

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None


class LLMProvider:
    """
    Unified interface for multiple LLM providers.
    
    Supports:
    - Google Gemini (via langchain-google-genai)
    - Anthropic Claude (via langchain-anthropic)
    - OpenAI (via langchain-openai)
    - OpenRouter (via langchain-openai with custom base_url)
    - Groq (via langchain-openai with custom base_url)
    - Together AI (via langchain-openai with custom base_url)
    """
    
    @staticmethod
    def create_llm(
        provider: str,
        model_name: Optional[str] = None,
        temperature: float = 0.1,
        **kwargs
    ) -> BaseChatModel:
        """
        Create an LLM instance from the specified provider.
        
        Args:
            provider: Provider name ("google", "anthropic", "openai", "openrouter", "groq", "together")
            model_name: Model name (defaults to provider's best model)
            temperature: Temperature for generation
            **kwargs: Additional provider-specific arguments
        
        Returns:
            BaseChatModel instance
        """
        provider_lower = provider.lower()
        
        if provider_lower == "google":
            return LLMProvider._create_google_llm(model_name, temperature, **kwargs)
        elif provider_lower == "anthropic":
            return LLMProvider._create_anthropic_llm(model_name, temperature, **kwargs)
        elif provider_lower == "openai":
            return LLMProvider._create_openai_llm(model_name, temperature, **kwargs)
        elif provider_lower == "openrouter":
            return LLMProvider._create_openrouter_llm(model_name, temperature, **kwargs)
        elif provider_lower == "groq":
            return LLMProvider._create_groq_llm(model_name, temperature, **kwargs)
        elif provider_lower == "together":
            return LLMProvider._create_together_llm(model_name, temperature, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    @staticmethod
    def _create_google_llm(model_name: Optional[str], temperature: float, **kwargs) -> BaseChatModel:
        """Create Google Gemini LLM."""
        if ChatGoogleGenerativeAI is None:
            raise ImportError("langchain-google-genai not installed. Install with: pip install langchain-google-genai")
        
        api_key = kwargs.get("api_key") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        
        # Use gemini-3-pro-preview as default (latest and most capable)
        return ChatGoogleGenerativeAI(
            model=model_name or "gemini-3-pro-preview",
            temperature=temperature,
            google_api_key=api_key
        )
    
    @staticmethod
    def _create_anthropic_llm(model_name: Optional[str], temperature: float, **kwargs) -> BaseChatModel:
        """Create Anthropic Claude LLM."""
        if ChatAnthropic is None:
            raise ImportError("langchain-anthropic not installed. Install with: pip install langchain-anthropic")
        
        api_key = kwargs.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
        return ChatAnthropic(
            model=model_name or "claude-3-5-sonnet-20241022",
            temperature=temperature,
            anthropic_api_key=api_key
        )
    
    @staticmethod
    def _create_openai_llm(model_name: Optional[str], temperature: float, **kwargs) -> BaseChatModel:
        """Create OpenAI LLM."""
        if ChatOpenAI is None:
            raise ImportError("langchain-openai not installed. Install with: pip install langchain-openai")
        
        api_key = kwargs.get("api_key") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        return ChatOpenAI(
            model=model_name or "gpt-4o",
            temperature=temperature,
            api_key=api_key
        )
    
    @staticmethod
    def _create_openrouter_llm(model_name: Optional[str], temperature: float, **kwargs) -> BaseChatModel:
        """Create OpenRouter LLM."""
        if ChatOpenAI is None:
            raise ImportError("langchain-openai not installed. Install with: pip install langchain-openai")
        
        api_key = kwargs.get("api_key") or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment")
        
        # OpenRouter uses OpenAI-compatible API
        return ChatOpenAI(
            model=model_name or "anthropic/claude-3.5-sonnet",
            temperature=temperature,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": kwargs.get("app_url", "https://github.com/devadigapratham/sensei"),
                "X-Title": "Sensei Research Scientist"
            }
        )
    
    @staticmethod
    def _create_groq_llm(model_name: Optional[str], temperature: float, **kwargs) -> BaseChatModel:
        """Create Groq LLM."""
        if ChatOpenAI is None:
            raise ImportError("langchain-openai not installed. Install with: pip install langchain-openai")
        
        api_key = kwargs.get("api_key") or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment")
        
        # Groq uses OpenAI-compatible API
        # Default to llama-3.3-70b-versatile (latest and most capable)
        return ChatOpenAI(
            model=model_name or "llama-3.3-70b-versatile",
            temperature=temperature,
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
    
    @staticmethod
    def _create_together_llm(model_name: Optional[str], temperature: float, **kwargs) -> BaseChatModel:
        """Create Together AI LLM."""
        if ChatOpenAI is None:
            raise ImportError("langchain-openai not installed. Install with: pip install langchain-openai")
        
        api_key = kwargs.get("api_key") or os.getenv("TOGETHER_API_KEY")
        if not api_key:
            raise ValueError("TOGETHER_API_KEY not found in environment")
        
        # Together AI uses OpenAI-compatible API
        return ChatOpenAI(
            model=model_name or "meta-llama/Llama-3-70b-chat-hf",
            temperature=temperature,
            api_key=api_key,
            base_url="https://api.together.xyz/v1"
        )


# Available models per provider
AVAILABLE_MODELS = {
    "google": [
        "gemini-2.5-flash",  # Free tier - recommended
        "gemini-3-flash-preview",  # Free tier
        "gemini-2.5-pro",  # Paid tier
        "gemini-3-pro-preview",  # Paid tier
        "gemini-2.0-flash-exp",
    ],
    "anthropic": [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
    ],
    "openai": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
    ],
    "openrouter": [
        "anthropic/claude-3.5-sonnet",
        "openai/gpt-4o",
        "google/gemini-pro-1.5",
        "meta-llama/llama-3.1-70b-instruct",
        "mistralai/mixtral-8x7b-instruct",
    ],
    "groq": [
        # Llama Models
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "meta-llama/llama-4-maverick-17b-128e-instruct",
        "meta-llama/llama-4-scout-17b-16e-instruct",
        # OpenAI OSS Models
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        # Qwen Models
        "qwen/qwen3-32b",
        # Groq Compound Models
        "groq/compound",
        "groq/compound-mini",
        # Kimi Models
        "moonshotai/kimi-k2-instruct",
        "moonshotai/kimi-k2-instruct-0905",
        # Other Models
        "allam-2-7b",
    ],
    "together": [
        "meta-llama/Llama-3-70b-chat-hf",
        "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "google/gemma-2-27b-it",
        "Qwen/Qwen2.5-72B-Instruct",
    ],
}

