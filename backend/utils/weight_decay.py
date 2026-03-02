"""
Weight decay calculation for retry mechanism
Uses exponential decay for confidence weighting
"""
import math
from config import settings


def compute_weight(
    initial_weight: float,
    retry_count: int,
    decay_factor: float = None
) -> float:
    """
    Compute weight using exponential decay
    
    Formula: W_n = W_0 * exp(-decay_factor * retry_count)
    
    Args:
        initial_weight: Initial weight value (W_0)
        retry_count: Number of retries (n)
        decay_factor: Decay rate (default from config)
        
    Returns:
        Decayed weight value
    """
    if decay_factor is None:
        decay_factor = settings.DECAY_FACTOR
    
    weight = initial_weight * math.exp(-decay_factor * retry_count)
    return weight


def compute_adjusted_temperature(
    base_temperature: float,
    retry_count: int,
    decay_factor: float = None
) -> float:
    """
    Compute adjusted LLM temperature based on retry count
    Increases temperature on retries to encourage different outputs
    
    Args:
        base_temperature: Base temperature value
        retry_count: Number of retries
        decay_factor: Decay rate (default from config)
        
    Returns:
        Adjusted temperature value
    """
    if decay_factor is None:
        decay_factor = settings.DECAY_FACTOR
    
    # Inverse decay - temperature increases with retries
    adjustment = 1 + (0.1 * retry_count)  # Increase by 0.1 per retry
    adjusted_temp = min(base_temperature * adjustment, 1.0)  # Cap at 1.0
    
    return adjusted_temp


def compute_retrieval_depth(
    base_depth: int,
    retry_count: int,
    max_depth: int = 10
) -> int:
    """
    Compute adjusted retrieval depth for retries
    Increases number of retrieved chunks on retries
    
    Args:
        base_depth: Base number of chunks to retrieve
        retry_count: Number of retries
        max_depth: Maximum depth allowed
        
    Returns:
        Adjusted retrieval depth
    """
    adjusted_depth = base_depth + (2 * retry_count)  # Add 2 chunks per retry
    return min(adjusted_depth, max_depth)
