import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # LLM Provider Selection
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")  # Options: "ollama" or "azure"
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5-mini-2")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
    AZURE_OPENAI_MODEL: str = os.getenv("AZURE_OPENAI_MODEL", "gpt-5-mini")
    
    # ChromaDB Configuration
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "../chroma_db")
    CHROMA_COLLECTION_NAME: str = "financial_docs"
    
    # Chunking Configuration
    CHUNK_SIZE: int = 900  # tokens
    CHUNK_OVERLAP: int = 150  # tokens
    OCR_THRESHOLD: int = 1000  # minimum chars before OCR fallback
    
    # Agent Configuration
    RELEVANCE_THRESHOLD: float = 0.7  # Confidence threshold
    MAX_RETRIES: int = 3  # Maximum number of retry attempts (total attempts = MAX_RETRIES)
    DECAY_FACTOR: float = 0.5  # Exponential decay factor
    
    # Retrieval Configuration
    TOP_K_CHUNKS: int = 5
    
    # Storage
    DATA_DIR: Path = Path("./data")
    QUERY_HISTORY_FILE: Path = DATA_DIR / "query_history.json"
    UPLOADS_DIR: Path = Path("../uploads")
    
    # LLM Configuration
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 2000
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Initialize settings
settings = Settings()

# Create necessary directories
settings.DATA_DIR.mkdir(exist_ok=True)
settings.UPLOADS_DIR.mkdir(exist_ok=True)
