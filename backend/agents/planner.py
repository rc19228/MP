"""
Planner Agent
Classifies user intent and determines required analysis
"""
from typing import Dict
from utils.llm_client import get_llm_client


class PlannerAgent:
    def __init__(self):
        """
        Initialize Planner Agent
        """
        self.llm = get_llm_client()
        self.system_prompt = """You are a financial analysis planning assistant.
Your task is to classify the user's query intent and determine what analysis is needed.

Classify intent into one of these categories:
- summarization: User wants a summary of financial information
- ratio_analysis: User wants financial ratios calculated
- trend_analysis: User wants trend analysis over time
- risk_analysis: User wants risk assessment

Also identify:
- metrics_required: List of specific metrics needed (e.g., revenue, profit, debt)
- time_range: Relevant time period (e.g., "2023", "Q1 2024", "last year")

IMPORTANT: Return ONLY valid JSON, no markdown formatting."""
    
    def plan(self, user_query: str) -> Dict:
        """
        Analyze user query and create execution plan
        
        Args:
            user_query: User's question
            
        Returns:
            Dictionary with intent, metrics_required, and time_range
        """
        prompt = f"""Analyze this financial query and classify it:

Query: {user_query}

Return JSON with this structure:
{{
  "intent": "summarization|ratio_analysis|trend_analysis|risk_analysis",
  "metrics_required": ["metric1", "metric2"],
  "time_range": "relevant time period or null"
}}

JSON response:"""
        
        result = self.llm.generate_json(
            prompt=prompt,
            system=self.system_prompt,
            temperature=0.1
        )
        
        # Validate and set defaults
        if "error" in result:
            print(f"Planner error: {result.get('error')}")
            return self._default_plan()
        
        # Ensure required fields
        plan = {
            "intent": result.get("intent", "summarization"),
            "metrics_required": result.get("metrics_required", []),
            "time_range": result.get("time_range", None)
        }
        
        return plan
    
    def _default_plan(self) -> Dict:
        """
        Return default plan when parsing fails
        
        Returns:
            Default plan dictionary
        """
        return {
            "intent": "summarization",
            "metrics_required": [],
            "time_range": None
        }


def create_plan(user_query: str) -> Dict:
    """
    Convenience function to create plan
    
    Args:
        user_query: User's question
        
    Returns:
        Execution plan
    """
    planner = PlannerAgent()
    return planner.plan(user_query)
