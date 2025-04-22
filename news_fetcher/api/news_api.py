"""
News API Client

This module provides a client for interacting with the News API.
"""
import logging
from typing import Any, Dict, List, Optional, Callable

from news_fetcher.api.base import BaseAPIClient
from news_fetcher.config.settings import config

# Set up logging
logger = logging.getLogger(__name__)


class NewsAPIClient(BaseAPIClient):
    """Client for interacting with the News API."""

    def __init__(
        self,
        api_key: str = config.NEWS_API_KEY,
        base_url: str = "https://newsapi.org/v2",
        timeout: int = config.REQUEST_TIMEOUT,
        max_retries: int = config.MAX_RETRIES,
        retry_delay: int = config.RETRY_DELAY
    ):
        """
        Initialize the News API client.

        Args:
            api_key: The API key for authentication.
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

    def _validate_news_response(self, response: Dict[str, Any]) -> bool:
        """
        Validate the response from the News API.

        Args:
            response: The response from the API.

        Returns:
            True if the response is valid, False otherwise.
        """
        if "status" not in response:
            logger.error("Response missing 'status' field")
            return False

        if response["status"] != "ok":
            logger.error(f"API returned error status: {response.get('status')}")
            return False

        if "articles" not in response:
            logger.error("Response missing 'articles' field")
            return False

        return True

    def get_top_headlines(
        self,
        country: str = "us",
        category: Optional[str] = None,
        q: Optional[str] = None,
        page_size: int = 20,
        page: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get top headlines from the News API.

        Args:
            country: The 2-letter ISO 3166-1 code of the country.
            category: The category to get headlines for.
            q: Keywords or phrases to search for.
            page_size: The number of results to return per page (max 100).
            page: The page number to return.

        Returns:
            A list of article dictionaries.

        Raises:
            RequestException: If the request fails after all retries.
            ValueError: If the response validation fails.
        """
        params = {
            "country": country,
            "pageSize": page_size,
            "page": page,
            "apiKey": self.api_key
        }

        if category:
            params["category"] = category

        if q:
            params["q"] = q

        try:
            response = self.get(
                endpoint="top-headlines",
                params=params,
                validator=self._validate_news_response
            )
            return response.get("articles", [])
        except Exception as e:
            logger.error(f"Error fetching top headlines: {str(e)}")
            return []

    def get_everything(
        self,
        q: Optional[str] = None,
        sources: Optional[str] = None,
        domains: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        language: str = "en",
        sort_by: str = "publishedAt",
        page_size: int = 20,
        page: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get everything from the News API.

        Args:
            q: Keywords or phrases to search for.
            sources: A comma-separated string of identifiers for the news sources or blogs.
            domains: A comma-separated string of domains to restrict the search to.
            from_date: A date in ISO 8601 format (e.g. 2023-12-25).
            to_date: A date in ISO 8601 format (e.g. 2023-12-25).
            language: The 2-letter ISO-639-1 code of the language.
            sort_by: The order to sort the articles in (relevancy, popularity, publishedAt).
            page_size: The number of results to return per page (max 100).
            page: The page number to return.

        Returns:
            A list of article dictionaries.

        Raises:
            RequestException: If the request fails after all retries.
            ValueError: If the response validation fails.
        """
        params = {
            "language": language,
            "sortBy": sort_by,
            "pageSize": page_size,
            "page": page,
            "apiKey": self.api_key
        }

        if q:
            params["q"] = q

        if sources:
            params["sources"] = sources

        if domains:
            params["domains"] = domains

        if from_date:
            params["from"] = from_date

        if to_date:
            params["to"] = to_date

        try:
            response = self.get(
                endpoint="everything",
                params=params,
                validator=self._validate_news_response
            )
            return response.get("articles", [])
        except Exception as e:
            logger.error(f"Error fetching everything: {str(e)}")
            return []


# Create a singleton instance for easy import
news_api_client = NewsAPIClient()
