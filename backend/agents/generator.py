"""
Generator Agent
Generates structured financial analysis using LLM
"""
from typing import Dict
from utils.ollama_client import get_ollama_client
from config import settings


class GeneratorAgent:
    def __init__(self):
        """
        Initialize Generator Agent
        """
        self.ollama = get_ollama_client()
        self.system_prompt = """You are a financial analysis expert.
Your task is to generate structured financial analysis based ONLY on the provided context.

CRITICAL RULES:
1. Use ONLY information from the provided context
2. Do NOT invent or assume numbers
3. If information is missing, state "Information not available"
4. Be precise and cite specific figures from the context
5. Provide a confidence score (0.0-1.0) based on information completeness

Return ONLY valid JSON with no markdown formatting."""
    
    def generate(
        self,
        query: str,
        context: str,
        intent: str,
        computed_metrics: Dict = None,
        temperature: float = None
    ) -> Dict:
        """
        Generate financial analysis response
        
        Args:
            query: User's question
            context: Retrieved document context
            intent: Analysis intent from Planner
            computed_metrics: Computed metrics from Analyzer
            temperature: LLM temperature
            
        Returns:
            Dictionary with executive_summary, analysis, risk_factors, and confidence
        """
        temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE
        
        # Build prompt based on intent
        metrics_text = ""
        if computed_metrics:
            metrics_text = f"\n\nComputed Metrics:\n{self._format_metrics(computed_metrics)}"
        
        prompt = f"""User Query: {query}

Analysis Intent: {intent}

Context from Financial Documents:
{context}{metrics_text}

Based on the above context, provide a comprehensive financial analysis.

Return JSON with this exact structure:
{{
  "executive_summary": "Brief overview (2-3 sentences)",
  "analysis": "Detailed analysis addressing the query",
  "risk_factors": "Identified risks or concerns",
  "confidence": 0.85
}}

Set confidence based on:
- 0.9-1.0: All information available, clear answer
- 0.7-0.9: Most information available, minor gaps
- 0.5-0.7: Significant information gaps
- 0.0-0.5: Insufficient information

JSON response:"""
        
        result = self.ollama.generate_json(
            prompt=prompt,
            system=self.system_prompt,
            temperature=temperature,
            required_keys=["executive_summary", "analysis", "risk_factors", "confidence"],
            fallback_defaults={
                "executive_summary": "Information not available",
                "analysis": "Information not available",
                "risk_factors": "Information not available",
                "confidence": 0.0
            }
        )
        
        # Validate response
        if "error" in result:
            print(f"Generator error: {result.get('error')}")
            return self._default_response()
        
        # Ensure required fields
        exec_summary = result.get("executive_summary", "Unable to generate summary.")
        analysis = result.get("analysis", "Unable to generate analysis.")
        risk_factors = result.get("risk_factors", "Unable to identify risks.")
        
        if not isinstance(exec_summary, str):
            exec_summary = str(exec_summary)
        
        response = {
            "executive_summary": exec_summary,
            "analysis": analysis,
            "risk_factors": risk_factors,
            "confidence": float(result.get("confidence", 0.0))
        }
        
        # Add computed metrics if available
        if computed_metrics:
            response["computed_metrics"] = computed_metrics
        
        return response
    
    def _format_metrics(self, metrics: Dict) -> str:
        """
        Format computed metrics for prompt
        
        Args:
            metrics: Dictionary of computed metrics
            
        Returns:
            Formatted string
        """
        lines = []
        for key, value in metrics.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    lines.append(f"  {sub_key}: {sub_value}")
            else:
                lines.append(f"  {key}: {value}")
        
        return "\n".join(lines)
    
    def _default_response(self) -> Dict:
        """
        Return default response when generation fails
        
        Returns:
            Default response dictionary
        """
        return {
            "executive_summary": "Unable to generate analysis due to processing error.",
            "analysis": "The system encountered an error while processing the request.",
            "risk_factors": "Unable to assess risks.",
            "confidence": 0.0
        }


def generate_response(
    query: str,
    context: str,
    intent: str,
    computed_metrics: Dict = None,
    temperature: float = None
) -> Dict:
    """
    Convenience function to generate response
    
    Args:
        query: User's question
        context: Retrieved context
        intent: Analysis intent
        computed_metrics: Computed metrics
        temperature: LLM temperature
        
    Returns:
        Generated analysis
    """
    generator = GeneratorAgent()
    return generator.generate(query, context, intent, computed_metrics, temperature)
