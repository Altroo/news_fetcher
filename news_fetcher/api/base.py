"""
Base API Client

This module provides a base class for API clients with common functionality.
"""
import time
import logging
from typing import Any, Dict, Optional, Callable
import requests
from requests.exceptions import RequestException

from news_fetcher.config.settings import config

# Set up logging
logger = logging.getLogger(__name__)


class BaseAPIClient:
    """Base class for API clients with retry and rate limiting functionality."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = config.REQUEST_TIMEOUT,
        max_retries: int = config.MAX_RETRIES,
        retry_delay: int = config.RETRY_DELAY
    ):
        """
        Initialize the API client.

        Args:
            base_url: The base URL for the API.
            api_key: The API key for authentication.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts for failed requests.
            retry_delay: Delay between retry attempts in seconds.
        """
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()
        self._last_request_time = 0

    def _rate_limit(self, min_interval: float = 1.0) -> None:
        """
        Implement rate limiting by ensuring a minimum interval between requests.

        Args:
            min_interval: Minimum interval between requests in seconds.
        """
        current_time = time.time()
        elapsed = current_time - self._last_request_time
        
        if elapsed < min_interval:
            sleep_time = min_interval - elapsed
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
            
        self._last_request_time = time.time()

    def request_with_retries(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        validator: Optional[Callable[[Dict[str, Any]], bool]] = None
    ) -> Any | None:
        """
        Make an HTTP request with retry mechanism and response validation.

        Args:
            method: HTTP method (GET, POST, etc.).
            endpoint: API endpoint to call.
            headers: HTTP headers to include.
            params: Query parameters.
            json_data: JSON data for POST requests.
            validator: Function to validate the response.

        Returns:
            The JSON response from the API.

        Raises:
            RequestException: If the request fails after all retries.
            ValueError: If the response validation fails.
        """
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        
        # Apply rate limiting
        self._rate_limit()
        
        # Set default headers if not provided
        if headers is None:
            headers = {}
            
        # Add authorization if API key is available
        if self.api_key and "Authorization" not in headers:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    timeout=self.timeout
                )
                
                # Raise an exception for HTTP errors
                response.raise_for_status()
                
                # Parse JSON response
                data = response.json()
                
                # Validate response if validator is provided
                if validator and not validator(data):
                    raise ValueError("Response validation failed")
                    
                return data
                
            except (RequestException, ValueError) as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries + 1}): {str(e)}")
                
                if attempt < self.max_retries:
                    # Calculate exponential backoff delay
                    backoff_delay = self.retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {backoff_delay} seconds...")
                    time.sleep(backoff_delay)
                    return None
                else:
                    logger.error(f"Request failed after {self.max_retries + 1} attempts")
                    raise
        return None

    def get(
        self,
        endpoint: str = "",
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        validator: Optional[Callable[[Dict[str, Any]], bool]] = None
    ) -> Dict[str, Any]:
        """
        Make a GET request.

        Args:
            endpoint: API endpoint to call.
            params: Query parameters.
            headers: HTTP headers to include.
            validator: Function to validate the response.

        Returns:
            The JSON response from the API.
        """
        return self.request_with_retries(
            method="GET",
            endpoint=endpoint,
            headers=headers,
            params=params,
            validator=validator
        )
        
    def post(
        self,
        endpoint: str = "",
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        validator: Optional[Callable[[Dict[str, Any]], bool]] = None
    ) -> Dict[str, Any]:
        """
        Make a POST request.

        Args:
            endpoint: API endpoint to call.
            json_data: JSON data for the request.
            headers: HTTP headers to include.
            validator: Function to validate the response.

        Returns:
            The JSON response from the API.
        """
        return self.request_with_retries(
            method="POST",
            endpoint=endpoint,
            headers=headers,
            json_data=json_data,
            validator=validator
        )