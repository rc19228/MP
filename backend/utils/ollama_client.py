"""
Ollama HTTP API client for LLM interactions
"""
import httpx
import json
import re
from typing import Dict, Optional
from config import settings


class OllamaClient:
    def __init__(self, base_url: str = None, model: str = None):
        """
        Initialize Ollama client
        
        Args:
            base_url: Ollama API base URL
            model: Model name to use
        """
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL
        self.generate_endpoint = f"{self.base_url}/api/generate"
        self.embeddings_endpoint = f"{self.base_url}/api/embeddings"
    
    def generate(
        self,
        prompt: str,
        temperature: float = None,
        max_tokens: int = None,
        system: Optional[str] = None,
        stream: bool = False
    ) -> Dict:
        """
        Generate text using Ollama
        
        Args:
            prompt: User prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system: System prompt
            stream: Whether to stream response
            
        Returns:
            Response dictionary with 'response' and 'context'
        """
        temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE
        max_tokens = max_tokens if max_tokens is not None else settings.LLM_MAX_TOKENS
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        if system:
            payload["system"] = system
        
        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(
                    self.generate_endpoint,
                    json=payload
                )
                response.raise_for_status()
                
                if stream:
                    # For streaming, return the response object
                    return response
                else:
                    # For non-streaming, parse the response
                    result = response.json()
                    return {
                        "response": result.get("response", ""),
                        "context": result.get("context", [])
                    }
        
        except httpx.HTTPError as e:
            print(f"HTTP error calling Ollama: {e}")
            return {
                "response": "",
                "context": [],
                "error": str(e)
            }
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return {
                "response": "",
                "context": [],
                "error": str(e)
            }
    
    def generate_json(
        self,
        prompt: str,
        temperature: float = None,
        system: Optional[str] = None,
        required_keys: Optional[list] = None,
        fallback_defaults: Optional[Dict] = None
    ) -> Dict:
        """
        Generate JSON response using Ollama
        
        Args:
            prompt: User prompt (should request JSON output)
            temperature: Sampling temperature
            system: System prompt
            
        Returns:
            Parsed JSON dictionary
        """
        result = self.generate(
            prompt=prompt,
            temperature=temperature,
            system=system
        )
        
        response_text = result.get("response", "")
        
        # Try to parse JSON from response
        try:
            json_text = self._extract_json_block(response_text)
            parsed = json.loads(json_text)
            parsed = self._ensure_required_keys(parsed, required_keys, fallback_defaults)
            return parsed
        
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON from response: {e}")
            print(f"Response text: {response_text}")

            # Attempt lightweight cleanup first (remove JS-style comments and trailing commas)
            try:
                sanitized = self._sanitize_json_text(self._extract_json_block(response_text))
                repaired = json.loads(sanitized)
                repaired = self._ensure_required_keys(repaired, required_keys, fallback_defaults)
                print("Recovered JSON via sanitizer fallback")
                return repaired
            except Exception:
                pass

            # SOP fallback: ask LLM to correct malformed JSON into strict JSON only
            repaired = self._repair_json_with_llm(
                raw_response=response_text,
                required_keys=required_keys,
                fallback_defaults=fallback_defaults
            )

            if repaired is not None:
                return repaired

            return {
                "error": "Failed to parse JSON",
                "raw_response": response_text
            }

    def _extract_json_block(self, response_text: str) -> str:
        """
        Extract likely JSON content from plain text or fenced blocks
        """
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            return response_text[json_start:json_end].strip()

        if "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            return response_text[json_start:json_end].strip()

        return response_text.strip()

    def _sanitize_json_text(self, json_text: str) -> str:
        """
        Apply safe cleanups for common invalid JSON patterns from LLM output
        """
        # Remove line comments //...
        json_text = re.sub(r"//.*", "", json_text)
        # Remove block comments /* ... */
        json_text = re.sub(r"/\*.*?\*/", "", json_text, flags=re.DOTALL)
        # Remove trailing commas before closing object/array
        json_text = re.sub(r",\s*([}\]])", r"\1", json_text)
        return json_text.strip()

    def _ensure_required_keys(
        self,
        payload: Dict,
        required_keys: Optional[list],
        fallback_defaults: Optional[Dict]
    ) -> Dict:
        if not isinstance(payload, dict):
            return payload

        if not required_keys:
            return payload

        defaults = fallback_defaults or {}
        for key in required_keys:
            if key not in payload:
                payload[key] = defaults.get(key)

        return payload

    def _repair_json_with_llm(
        self,
        raw_response: str,
        required_keys: Optional[list] = None,
        fallback_defaults: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Structured Output Parser fallback: repair malformed JSON with strict output rules
        """
        keys_text = ""
        if required_keys:
            keys_text = "Required top-level keys: " + ", ".join(required_keys)

        repair_prompt = f"""You are a Structured Output Parser (SOP).
Fix the malformed JSON below and return STRICT valid JSON only.

Rules:
- Output ONLY JSON (no markdown, no explanations)
- Remove comments and invalid tokens
- Keep the original meaning and values where possible
- If a required key is missing, add it with a sensible default
{keys_text}

Malformed content:
{raw_response}
"""

        repair_result = self.generate(
            prompt=repair_prompt,
            temperature=0.0,
            max_tokens=settings.LLM_MAX_TOKENS
        )

        repaired_text = repair_result.get("response", "")

        try:
            repaired_json_text = self._extract_json_block(repaired_text)
            repaired_json_text = self._sanitize_json_text(repaired_json_text)
            parsed = json.loads(repaired_json_text)
            parsed = self._ensure_required_keys(parsed, required_keys, fallback_defaults)
            print("Recovered JSON via SOP fallback")
            return parsed
        except Exception as e:
            print(f"SOP fallback failed: {e}")
            return None
    
    def get_embeddings(self, text: str) -> list:
        """
        Get embeddings for text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        payload = {
            "model": self.model,
            "prompt": text
        }
        
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    self.embeddings_endpoint,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                return result.get("embedding", [])
        
        except Exception as e:
            print(f"Error getting embeddings: {e}")
            return []


# Singleton instance
_ollama_client = None


def get_ollama_client() -> OllamaClient:
    """
    Get or create Ollama client singleton
    
    Returns:
        OllamaClient instance
    """
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client
