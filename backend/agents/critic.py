"""
Critic Agent
Evaluates response quality and triggers retries with weight decay
"""
import json
from pathlib import Path
from typing import Dict
from datetime import datetime
from config import settings
from utils.weight_decay import (
    compute_weight,
    compute_adjusted_temperature,
    compute_retrieval_depth
)


class CriticAgent:
    def __init__(self):
        """
        Initialize Critic Agent
        """
        self.threshold = settings.RELEVANCE_THRESHOLD
        self.max_retries = settings.MAX_RETRIES
        self.query_history_file = settings.QUERY_HISTORY_FILE
        
        # Ensure history file exists
        if not self.query_history_file.exists():
            self._init_history_file()
    
    def evaluate(
        self,
        response: Dict,
        query: str,
        retry_count: int = 0
    ) -> Dict:
        """
        Evaluate response quality and decide on retry
        
        Args:
            response: Generated response from Generator
            query: Original user query
            retry_count: Current retry count
            
        Returns:
            Dictionary with evaluation results and retry decision
        """
        confidence = response.get("confidence", 0.0)
        
        evaluation = {
            "confidence": confidence,
            "meets_threshold": confidence >= self.threshold,
            "retry_count": retry_count,
            "should_retry": False,
            "weight": 1.0,
            "adjusted_temperature": settings.LLM_TEMPERATURE,
            "adjusted_retrieval_depth": settings.TOP_K_CHUNKS
        }
        
        # Determine if retry is needed
        if confidence < self.threshold and retry_count < self.max_retries:
            evaluation["should_retry"] = True
            
            # Compute weight decay
            weight = compute_weight(
                initial_weight=1.0,
                retry_count=retry_count + 1,
                decay_factor=settings.DECAY_FACTOR
            )
            evaluation["weight"] = weight
            
            # Adjust temperature for next attempt
            adjusted_temp = compute_adjusted_temperature(
                base_temperature=settings.LLM_TEMPERATURE,
                retry_count=retry_count + 1
            )
            evaluation["adjusted_temperature"] = adjusted_temp
            
            # Adjust retrieval depth for next attempt
            adjusted_depth = compute_retrieval_depth(
                base_depth=settings.TOP_K_CHUNKS,
                retry_count=retry_count + 1
            )
            evaluation["adjusted_retrieval_depth"] = adjusted_depth
        
        # Log to history
        self._log_to_history(query, response, evaluation)
        
        return evaluation
    
    def _init_history_file(self):
        """
        Initialize query history JSON file
        """
        with open(self.query_history_file, 'w') as f:
            json.dump([], f)
    
    def _log_to_history(self, query: str, response: Dict, evaluation: Dict):
        """
        Log query, response, and evaluation to history file
        
        Args:
            query: User query
            response: Generated response
            evaluation: Evaluation results
        """
        try:
            # Load existing history
            with open(self.query_history_file, 'r') as f:
                history = json.load(f)
            
            # Add new entry
            entry = {
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "confidence": evaluation["confidence"],
                "retry_count": evaluation["retry_count"],
                "weight": evaluation["weight"],
                "meets_threshold": evaluation["meets_threshold"],
                "executive_summary": response.get("executive_summary", "")
            }
            
            history.append(entry)
            
            # Save back to file
            with open(self.query_history_file, 'w') as f:
                json.dump(history, f, indent=2)
        
        except Exception as e:
            print(f"Error logging to history: {e}")
    
    def get_history(self, limit: int = 10) -> list:
        """
        Get recent query history
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of recent history entries
        """
        try:
            with open(self.query_history_file, 'r') as f:
                history = json.load(f)
            
            # Return most recent entries
            return history[-limit:]
        
        except Exception as e:
            print(f"Error reading history: {e}")
            return []


def evaluate_response(
    response: Dict,
    query: str,
    retry_count: int = 0
) -> Dict:
    """
    Convenience function to evaluate response
    
    Args:
        response: Generated response
        query: User query
        retry_count: Current retry count
        
    Returns:
        Evaluation results
    """
    critic = CriticAgent()
    return critic.evaluate(response, query, retry_count)
