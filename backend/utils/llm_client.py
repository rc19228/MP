"""
Unified LLM client factory
Provides a single interface to work with different LLM providers (Ollama, Azure OpenAI, etc.)
"""
from typing import Union
from config import settings
from utils.ollama_client import OllamaClient, get_ollama_client
from utils.azure_openai_client import AzureOpenAIClient, get_azure_openai_client


# Type alias for any supported LLM client
LLMClient = Union[OllamaClient, AzureOpenAIClient]


def get_llm_client() -> LLMClient:
    """
    Get the appropriate LLM client based on settings
    
    Returns:
        LLM client instance (OllamaClient or AzureOpenAIClient)
    """
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "azure":
        print(f"Using Azure OpenAI: {settings.AZURE_OPENAI_DEPLOYMENT}")
        return get_azure_openai_client()
    elif provider == "ollama":
        print(f"Using Ollama: {settings.OLLAMA_MODEL}")
        return get_ollama_client()
    else:
        raise ValueError(
            f"Unknown LLM provider: {provider}. "
            f"Supported providers: 'ollama', 'azure'"
        )


def get_provider_info() -> dict:
    """
    Get information about the current LLM provider
    
    Returns:
        Dictionary with provider information
    """
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "azure":
        return {
            "provider": "Azure OpenAI",
            "endpoint": settings.AZURE_OPENAI_ENDPOINT,
            "deployment": settings.AZURE_OPENAI_DEPLOYMENT,
            "model": settings.AZURE_OPENAI_MODEL,
            "api_version": settings.AZURE_OPENAI_API_VERSION
        }
    elif provider == "ollama":
        return {
            "provider": "Ollama",
            "base_url": settings.OLLAMA_BASE_URL,
            "model": settings.OLLAMA_MODEL
        }
    else:
        return {
            "provider": "Unknown",
            "error": f"Unknown provider: {provider}"
        }
