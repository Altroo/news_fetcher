"""
OpenRouter API Client

This module provides a client for interacting with the OpenRouter API for text generation.
"""
import logging
from typing import Any, Dict, List, Optional, Callable

from news_fetcher.api.base import BaseAPIClient
from news_fetcher.config.settings import config

# Set up logging
logger = logging.getLogger(__name__)


class OpenRouterAPIClient(BaseAPIClient):
    """Client for interacting with the OpenRouter API."""

    def __init__(
        self,
        api_key: str = config.OPENROUTER_API_KEY,
        engine_id: str = config.OPENROUTER_ENGINE_ID,
        base_url: str = "https://api.openrouter.ai/v1",
        timeout: int = config.REQUEST_TIMEOUT,
        max_retries: int = config.MAX_RETRIES,
        retry_delay: int = config.RETRY_DELAY
    ):
        """
        Initialize the OpenRouter API client.

        Args:
            api_key: The API key for authentication.
            engine_id: The engine/model ID to use.
            base_url: The base URL for the API.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts for failed requests.
            retry_delay: Delay between retry attempts in seconds.
        """
        super().__init__(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay
        )
        self.engine_id = engine_id

    def _validate_completion_response(self, response: Dict[str, Any]) -> bool:
        """
        Validate the response from the OpenRouter API.

        Args:
            response: The response from the API.

        Returns:
            True if the response is valid, False otherwise.
        """
        if "choices" not in response:
            logger.error("Response missing 'choices' field")
            return False

        if not response["choices"]:
            logger.error("Response contains empty 'choices' array")
            return False

        if "text" not in response["choices"][0]:
            logger.error("Response missing 'text' field in first choice")
            return False

        return True

    def generate_completion(
        self,
        prompt: str,
        max_tokens: int = config.MAX_TOKENS,
        temperature: float = config.TEMPERATURE,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stop: Optional[List[str]] = None
    ) -> str:
        """
        Generate a completion using the OpenRouter API.

        Args:
            prompt: The prompt to generate a completion for.
            max_tokens: The maximum number of tokens to generate.
            temperature: Controls randomness. Higher values mean more random completions.
            top_p: Controls diversity via nucleus sampling.
            frequency_penalty: Penalizes repeated tokens.
            presence_penalty: Penalizes repeated topics.
            stop: A list of strings that, when encountered, will stop generation.

        Returns:
            The generated text.

        Raises:
            RequestException: If the request fails after all retries.
            ValueError: If the response validation fails.
        """
        endpoint = f"engines/{self.engine_id}/completions"
        
        data = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty
        }
        
        if stop:
            data["stop"] = stop
            
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = self.post(
                endpoint=endpoint,
                json_data=data,
                headers=headers,
                validator=self._validate_completion_response
            )
            return response["choices"][0]["text"].strip()
        except Exception as e:
            logger.error(f"Error generating completion: {str(e)}")
            return "Summary not available."
            
    def summarize_article(self, article_text: str) -> str:
        """
        Summarize an article using the OpenRouter API.

        Args:
            article_text: The text of the article to summarize.

        Returns:
            The summary of the article.
        """
        prompt = f"Summarize the following article:\n\n{article_text}"
        return self.generate_completion(prompt=prompt)


# Create a singleton instance for easy import
openrouter_api_client = OpenRouterAPIClient()
