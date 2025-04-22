"""
Configuration Settings

This module manages application configuration using environment variables.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for managing application settings."""

    # News API settings
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    NEWS_API_URL: str = os.getenv(
        "NEWS_API_URL", 
        f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    )
    
    # OpenRouter API settings
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_ENGINE_ID: str = os.getenv("OPENROUTER_ENGINE_ID", "YOUR_ENGINE_ID")
    OPENROUTER_URL: str = os.getenv(
        "OPENROUTER_URL", 
        f"https://api.openrouter.ai/v1/engines/{OPENROUTER_ENGINE_ID}/completions"
    )
    
    # Content filtering settings
    THEMES: list[str] = os.getenv("THEMES", "technology,health,finance").split(",")
    
    # Output settings
    OUTPUT_FILE: str = os.getenv("OUTPUT_FILE", "news_summaries.txt")
    
    # Database settings
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # API request settings
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY: int = int(os.getenv("RETRY_DELAY", "1"))
    
    # Summarization settings
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "150"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.5"))
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate that all required configuration values are set.
        
        Returns:
            bool: True if all required values are set, False otherwise.
        """
        if not cls.NEWS_API_KEY:
            print("Error: NEWS_API_KEY is not set.")
            return False
            
        if not cls.OPENROUTER_API_KEY:
            print("Error: OPENROUTER_API_KEY is not set.")
            return False
            
        return True


# Create a singleton instance for easy import
config = Config()
