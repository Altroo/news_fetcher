"""
News Fetcher

This is the main entry point for the News Fetcher application.
"""
import argparse
import asyncio
import logging
import sys
from typing import List, Optional

from news_fetcher.app import news_fetcher
from news_fetcher.config.settings import config
from news_fetcher.utils.logging_config import configure_logging, get_logger
from news_fetcher.utils.async_utils import wait_for_background_task

# Configure logging
configure_logging(log_level=logging.INFO)

# Get logger
logger = get_logger("main")


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="News Fetcher - Fetch, filter, and summarize news articles")

    # Mode of operation
    parser.add_argument(
        "--async", 
        action="store_true", 
        dest="async_mode",
        help="Run in asynchronous mode"
    )
    parser.add_argument(
        "--background", 
        action="store_true", 
        help="Run in background mode"
    )

    # Configuration options
    parser.add_argument(
        "--themes", 
        type=str, 
        help="Comma-separated list of themes to filter by (overrides config)"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        help="Output file for summaries (overrides config)"
    )
    parser.add_argument(
        "--country", 
        type=str, 
        default="us",
        help="Country code for news articles (default: us)"
    )

    # Logging options
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug logging"
    )
    parser.add_argument(
        "--log-file", 
        type=str, 
        help="Log file path"
    )

    return parser.parse_args()


def apply_args(args: argparse.Namespace) -> None:
    """
    Apply command-line arguments to configuration.

    Args:
        args: Parsed command-line arguments.
    """
    # Apply themes if provided
    if args.themes:
        config.THEMES = args.themes.split(",")

    # Apply output file if provided
    if args.output:
        config.OUTPUT_FILE = args.output

    # Configure logging based on arguments
    log_level = logging.DEBUG if args.debug else logging.INFO
    configure_logging(log_level=log_level, log_file=args.log_file)


async def run_async() -> None:
    """Run the application in asynchronous mode."""
    logger.info("Running in asynchronous mode")
    future = news_fetcher.run_async()
    articles, summaries = await future
    logger.info(f"Processed {len(articles)} articles and generated {len(summaries)} summaries")


def run_sync() -> None:
    """Run the application in synchronous mode."""
    logger.info("Running in synchronous mode")
    articles, summaries = news_fetcher.run()
    logger.info(f"Processed {len(articles)} articles and generated {len(summaries)} summaries")


def run_background() -> None:
    """Run the application in background mode."""
    logger.info("Running in background mode")
    task_id = news_fetcher.run_background()
    logger.info(f"Background task started with ID: {task_id}")

    try:
        # Wait for the task to complete
        result = wait_for_background_task(task_id)
        if result["status"] == "completed":
            articles, summaries = result["result"]
            logger.info(f"Processed {len(articles)} articles and generated {len(summaries)} summaries")
        else:
            logger.error(f"Background task failed: {result['error']}")
    except KeyboardInterrupt:
        logger.info("Interrupted by user. Task continues in the background.")
        sys.exit(0)


def main() -> None:
    """Main entry point for the application."""
    # Parse command-line arguments
    args = parse_args()

    # Apply arguments to configuration
    apply_args(args)

    try:
        # Run in the appropriate mode
        if args.background:
            run_background()
        elif args.async_mode:
            asyncio.run(run_async())
        else:
            run_sync()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running application: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
