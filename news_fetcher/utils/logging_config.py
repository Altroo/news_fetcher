"""
Logging Configuration

This module provides utilities for configuring logging.
"""
import os
import sys
import logging
import traceback
from typing import Optional, Dict, Any, Callable, Type
from functools import wraps

# Default log format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_LEVEL = logging.INFO


def configure_logging(
    log_level: int = DEFAULT_LOG_LEVEL,
    log_format: str = DEFAULT_LOG_FORMAT,
    log_file: Optional[str] = None
) -> None:
    """
    Configure logging for the application.

    Args:
        log_level: The logging level (e.g., logging.INFO, logging.DEBUG).
        log_format: The format string for log messages.
        log_file: The file to write logs to. If None, logs are written to stderr.
    """
    # Create handlers
    handlers = []
    
    # Always add a console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(logging.Formatter(log_format))
    handlers.append(console_handler)
    
    # Add a file handler if a log file is specified
    if log_file:
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter(log_format))
            handlers.append(file_handler)
        except Exception as e:
            print(f"Error setting up log file: {str(e)}")
    
    # Configure the root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers
    )
    
    # Set the level for the news_fetcher logger
    logger = logging.getLogger("news_fetcher")
    logger.setLevel(log_level)
    
    # Suppress logs from other libraries
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    logger.info(f"Logging configured with level {logging.getLevelName(log_level)}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name: The name of the logger.

    Returns:
        A logger instance.
    """
    return logging.getLogger(f"news_fetcher.{name}")


class ErrorHandler:
    """Centralized error handling system."""

    @staticmethod
    def handle_error(
        error: Exception,
        logger: Optional[logging.Logger] = None,
        error_message: str = "An error occurred",
        raise_error: bool = False,
        default_return: Any = None
    ) -> Any:
        """
        Handle an error.

        Args:
            error: The exception that was raised.
            logger: The logger to use. If None, uses the root logger.
            error_message: A message to log with the error.
            raise_error: Whether to re-raise the error after handling.
            default_return: The value to return if the error is not re-raised.

        Returns:
            The default return value if the error is not re-raised.

        Raises:
            The original error if raise_error is True.
        """
        if logger is None:
            logger = logging.getLogger("news_fetcher")
            
        # Log the error
        logger.error(f"{error_message}: {str(error)}")
        logger.debug(f"Error details: {traceback.format_exc()}")
        
        # Re-raise the error if requested
        if raise_error:
            raise error
            
        return default_return

    @staticmethod
    def retry_on_error(
        max_retries: int = 3,
        retry_delay: int = 1,
        exceptions: tuple = (Exception,),
        logger: Optional[logging.Logger] = None,
        error_message: str = "Error occurred, retrying"
    ) -> Callable:
        """
        Decorator to retry a function on error.

        Args:
            max_retries: Maximum number of retry attempts.
            retry_delay: Delay between retry attempts in seconds.
            exceptions: Tuple of exceptions to catch and retry on.
            logger: The logger to use. If None, uses the root logger.
            error_message: A message to log with the error.

        Returns:
            A decorator function.
        """
        import time
        
        if logger is None:
            logger = logging.getLogger("news_fetcher")
        
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        if attempt < max_retries:
                            # Calculate exponential backoff delay
                            backoff_delay = retry_delay * (2 ** attempt)
                            logger.warning(
                                f"{error_message} (attempt {attempt + 1}/{max_retries + 1}): {str(e)}"
                            )
                            logger.info(f"Retrying in {backoff_delay} seconds...")
                            time.sleep(backoff_delay)
                            return None
                        else:
                            logger.error(f"Failed after {max_retries + 1} attempts: {str(e)}")
                            raise
                return None

            return wrapper
        return decorator


# Create a singleton instance for easy import
error_handler = ErrorHandler()
