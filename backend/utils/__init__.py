"""
Utility modules
"""
from .weight_decay import compute_weight, compute_adjusted_temperature, compute_retrieval_depth
from .ollama_client import OllamaClient, get_ollama_client

__all__ = [
    "compute_weight",
    "compute_adjusted_temperature",
    "compute_retrieval_depth",
    "OllamaClient",
    "get_ollama_client"
]
