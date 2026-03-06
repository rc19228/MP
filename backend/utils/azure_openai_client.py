"""
Azure OpenAI API client for LLM interactions
"""
import json
import re
from typing import Dict, Optional
from openai import AzureOpenAI
from config import settings


class AzureOpenAIClient:
    def __init__(
        self,
        endpoint: str = None,
        api_key: str = None,
        deployment: str = None,
        api_version: str = None
    ):
        """
        Initialize Azure OpenAI client
        
        Args:
            endpoint: Azure OpenAI endpoint URL
            api_key: Azure OpenAI API key
            deployment: Deployment name
            api_version: API version
        """
        self.endpoint = endpoint or settings.AZURE_OPENAI_ENDPOINT
        self.api_key = api_key or settings.AZURE_OPENAI_API_KEY
        self.deployment = deployment or settings.AZURE_OPENAI_DEPLOYMENT
        self.api_version = api_version or settings.AZURE_OPENAI_API_VERSION
        self.model = settings.AZURE_OPENAI_MODEL
        
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            api_version=self.api_version,
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
        )
    
    def generate(
        self,
        prompt: str,
        temperature: float = None,
        max_tokens: int = None,
        system: Optional[str] = None,
        stream: bool = False
    ) -> Dict:
        """
        Generate text using Azure OpenAI
        
        Args:
            prompt: User prompt
            temperature: Sampling temperature (Note: GPT-5-mini only supports default temperature=1)
            max_tokens: Maximum tokens to generate
            system: System prompt
            stream: Whether to stream response (not implemented)
            
        Returns:
            Response dictionary with 'response' and 'context'
        """
        max_tokens = max_tokens if max_tokens is not None else settings.LLM_MAX_TOKENS
        
        # Build messages list
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        # Note: GPT-5-mini only supports temperature=1 (default)
        # We omit the temperature parameter to use the model's default
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                # temperature parameter omitted - GPT-5-mini only supports default (1.0)
                max_completion_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                # For streaming, return the response object
                return response
            else:
                # For non-streaming, parse the response
                content = response.choices[0].message.content
                
                # Check if content is None or empty
                if content is None:
                    print("⚠️ Azure OpenAI returned None content")
                    content = ""
                
                return {
                    "response": content,
                    "context": [],  # Azure OpenAI doesn't provide context like Ollama
                    "model": self.deployment,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                }
        
        except Exception as e:
            print(f"❌ Error calling Azure OpenAI: {e}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
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
        Generate JSON response using Azure OpenAI
        
        Args:
            prompt: User prompt (should request JSON output)
            temperature: Sampling temperature
            system: System prompt
            required_keys: List of required keys in JSON response
            fallback_defaults: Default values for missing keys
            
        Returns:
            Parsed JSON dictionary
        """
        # Add JSON formatting instruction to system prompt
        json_system = (system or "") + "\n\nYou must respond with valid JSON only. Do not include markdown formatting or explanations."
        
        result = self.generate(
            prompt=prompt,
            temperature=temperature,
            system=json_system
        )
        
        response_text = result.get("response", "")
        
        # Log the raw response for debugging
        print(f"\n{'='*60}")
        print("Raw LLM Response:")
        print(f"{'='*60}")
        if not response_text or len(response_text.strip()) == 0:
            print("⚠️ WARNING: Empty response received from LLM!")
        else:
            print(response_text[:500] if len(response_text) > 500 else response_text)
            if len(response_text) > 500:
                print(f"... (truncated, total length: {len(response_text)} chars)")
        print(f"{'='*60}\n")
        
        # Try to parse JSON from response
        try:
            json_text = self._extract_json_block(response_text)
            parsed = json.loads(json_text)
            parsed = self._ensure_required_keys(parsed, required_keys, fallback_defaults)
            print("✓ Successfully parsed JSON on first attempt")
            return parsed
        
        except json.JSONDecodeError as e:
            print(f"✗ Failed to parse JSON from response: {e}")
            print(f"   Response length: {len(response_text)} characters")

            # Attempt lightweight cleanup first (remove JS-style comments and trailing commas)
            try:
                sanitized = self._sanitize_json_text(self._extract_json_block(response_text))
                repaired = json.loads(sanitized)
                repaired = self._ensure_required_keys(repaired, required_keys, fallback_defaults)
                print("✓ Recovered JSON via sanitizer fallback")
                print(f"   Sanitized JSON keys: {list(repaired.keys())}")
                return repaired
            except Exception as sanitize_error:
                print(f"✗ Sanitizer fallback failed: {sanitize_error}")

            # SOP fallback: ask LLM to correct malformed JSON into strict JSON only
            repaired = self._repair_json_with_llm(
                raw_response=response_text,
                required_keys=required_keys,
                fallback_defaults=fallback_defaults
            )

            if repaired is not None:
                print(f"✓ Final repaired JSON keys: {list(repaired.keys())}")
                return repaired

            print("✗ All JSON repair attempts failed")
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
            print("✓ Recovered JSON via SOP fallback")
            print(f"   SOP repaired response length: {len(repaired_text)} chars")
            print(f"   Repaired JSON preview: {str(parsed)[:200]}...")
            return parsed
        except Exception as e:
            print(f"✗ SOP fallback failed: {e}")
            print(f"   SOP raw response: {repaired_text[:300]}...")
            return None
    
    def get_embeddings(self, text: str) -> list:
        """
        Get embeddings for text using Azure OpenAI
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        try:
            # Azure OpenAI requires a separate embeddings deployment
            # For now, we'll use a placeholder - you may need to create an embeddings deployment
            # Common embedding models: text-embedding-ada-002, text-embedding-3-small, etc.
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"  # You may need to adjust this
            )
            return response.data[0].embedding
        
        except Exception as e:
            print(f"Error getting embeddings from Azure OpenAI: {e}")
            print("Note: You may need to create a separate embeddings deployment in Azure")
            return []


# Singleton instance
_azure_openai_client = None


def get_azure_openai_client() -> AzureOpenAIClient:
    """
    Get or create Azure OpenAI client singleton
    
    Returns:
        AzureOpenAIClient instance
    """
    global _azure_openai_client
    if _azure_openai_client is None:
        _azure_openai_client = AzureOpenAIClient()
    return _azure_openai_client
