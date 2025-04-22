"""
News Fetcher Application

This module provides the main application functionality for fetching news,
filtering by theme, generating summaries, and saving the results.
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple

from news_fetcher.config.settings import config
from news_fetcher.api.news_api import news_api_client
from news_fetcher.api.openrouter_api import openrouter_api_client
from news_fetcher.models.article import Article
from news_fetcher.models.summary import Summary
from news_fetcher.db.repository import ArticleRepository, SummaryRepository
from news_fetcher.utils.text_processing import (
    filter_articles_by_theme,
    get_article_text,
    clean_text
)
from news_fetcher.utils.file_operations import save_summaries_to_file
from news_fetcher.utils.logging_config import get_logger, error_handler
from news_fetcher.utils.async_utils import (
    run_async_tasks,
    run_in_background,
    wait_for_background_task
)

# Set up logging
logger = get_logger("app")


class NewsFetcher:
    """Main application class for fetching and processing news articles."""

    def __init__(self):
        """Initialize the NewsFetcher application."""
        self.validate_config()

    def validate_config(self) -> bool:
        """
        Validate the application configuration.

        Returns:
            True if the configuration is valid, False otherwise.
        """
        return config.validate()

    async def fetch_articles_async(self) -> List[Article]:
        """
        Fetch articles asynchronously.

        Returns:
            A list of Article objects.
        """
        # This is a placeholder for future async implementation
        # For now, we'll use the synchronous API client
        logger.info("Fetching articles")
        articles_data = news_api_client.get_top_headlines(country="us")
        return [Article.from_api_response(article) for article in articles_data]

    def fetch_articles(self) -> List[Article]:
        """
        Fetch articles synchronously.

        Returns:
            A list of Article objects.
        """
        try:
            logger.info("Fetching articles")
            articles_data = news_api_client.get_top_headlines(country="us")
            return [Article.from_api_response(article) for article in articles_data]
        except Exception as e:
            error_message = "Error fetching articles"
            return error_handler.handle_error(
                e, logger, error_message, raise_error=False, default_return=[]
            )

    def filter_articles(self, articles: List[Article], themes: List[str]) -> List[Article]:
        """
        Filter articles by themes.

        Args:
            articles: List of Article objects.
            themes: List of themes to filter by.

        Returns:
            Filtered list of Article objects.
        """
        try:
            logger.info(f"Filtering articles by themes: {', '.join(themes)}")
            
            # Convert Article objects to dictionaries for filtering
            articles_dict = [article.to_dict() for article in articles]
            
            # Filter articles by themes
            filtered_dict = filter_articles_by_theme(articles_dict, themes)
            
            # Convert back to Article objects and add themes
            filtered_articles = []
            for article_dict in filtered_dict:
                article = Article.from_dict(article_dict)
                article.themes = article_dict.get("matched_themes", [])
                filtered_articles.append(article)
                
            logger.info(f"Filtered {len(filtered_articles)} articles out of {len(articles)}")
            return filtered_articles
        except Exception as e:
            error_message = "Error filtering articles"
            return error_handler.handle_error(
                e, logger, error_message, raise_error=False, default_return=[]
            )

    def summarize_article(self, article: Article) -> Summary:
        """
        Generate a summary for an article.

        Args:
            article: The Article object to summarize.

        Returns:
            A Summary object.
        """
        try:
            logger.info(f"Summarizing article: {article.title}")
            
            # Get the article text
            article_text = article.content or article.description or ""
            article_text = clean_text(article_text)
            
            if not article_text:
                logger.warning(f"No content to summarize for article: {article.title}")
                return Summary(
                    article_id=article.id,
                    content="No content available for summarization.",
                    model_used="none"
                )
                
            # Generate summary
            summary_text = openrouter_api_client.summarize_article(article_text)
            
            # Create Summary object
            summary = Summary(
                article_id=article.id,
                content=summary_text,
                model_used=config.OPENROUTER_ENGINE_ID
            )
            
            return summary
        except Exception as e:
            error_message = f"Error summarizing article: {article.title}"
            return error_handler.handle_error(
                e, logger, error_message, raise_error=False,
                default_return=Summary(
                    article_id=article.id,
                    content="Error generating summary.",
                    model_used="error"
                )
            )

    async def summarize_articles_async(self, articles: List[Article]) -> List[Summary]:
        """
        Generate summaries for articles asynchronously.

        Args:
            articles: List of Article objects to summarize.

        Returns:
            List of Summary objects.
        """
        # This is a placeholder for future async implementation
        # For now, we'll use the synchronous method
        return [self.summarize_article(article) for article in articles]

    def summarize_articles_background(self, articles: List[Article]) -> int:
        """
        Generate summaries for articles in the background.

        Args:
            articles: List of Article objects to summarize.

        Returns:
            Task ID for the background task.
        """
        logger.info(f"Submitting background task to summarize {len(articles)} articles")
        
        def summarize_all():
            summaries = []
            for article in articles:
                summary = self.summarize_article(article)
                if summary:
                    # Save the summary to the database
                    SummaryRepository.save(summary)
                    summaries.append(summary)
            return summaries
            
        return run_in_background(summarize_all)

    def save_articles_to_db(self, articles: List[Article]) -> List[Article]:
        """
        Save articles to the database.

        Args:
            articles: List of Article objects to save.

        Returns:
            List of saved Article objects with IDs.
        """
        try:
            logger.info(f"Saving {len(articles)} articles to the database")
            saved_articles = []
            
            for article in articles:
                # Check if the article already exists
                existing = ArticleRepository.get_by_url(article.url)
                if existing:
                    logger.debug(f"Article already exists: {article.title}")
                    # Update the existing article
                    existing.themes = article.themes
                    ArticleRepository.save(existing)
                    saved_articles.append(existing)
                else:
                    # Save the new article
                    saved = ArticleRepository.save(article)
                    saved_articles.append(saved)
                    
            logger.info(f"Saved {len(saved_articles)} articles to the database")
            return saved_articles
        except Exception as e:
            error_message = "Error saving articles to the database"
            return error_handler.handle_error(
                e, logger, error_message, raise_error=False, default_return=[]
            )

    def save_summaries_to_db(self, summaries: List[Summary]) -> List[Summary]:
        """
        Save summaries to the database.

        Args:
            summaries: List of Summary objects to save.

        Returns:
            List of saved Summary objects with IDs.
        """
        try:
            logger.info(f"Saving {len(summaries)} summaries to the database")
            saved_summaries = []
            
            for summary in summaries:
                saved = SummaryRepository.save(summary)
                saved_summaries.append(saved)
                
            logger.info(f"Saved {len(saved_summaries)} summaries to the database")
            return saved_summaries
        except Exception as e:
            error_message = "Error saving summaries to the database"
            return error_handler.handle_error(
                e, logger, error_message, raise_error=False, default_return=[]
            )

    def save_summaries_to_file(self, summaries: List[Summary], articles: List[Article], filename: str) -> bool:
        """
        Save summaries to a file.

        Args:
            summaries: List of Summary objects to save.
            articles: List of Article objects corresponding to the summaries.
            filename: Name of the file to save to.

        Returns:
            True if the save was successful, False otherwise.
        """
        try:
            logger.info(f"Saving {len(summaries)} summaries to file: {filename}")
            
            # Create a dictionary mapping article IDs to titles
            article_titles = {article.id: article.title for article in articles}
            
            # Format summaries for output
            formatted_summaries = []
            for summary in summaries:
                article_title = article_titles.get(summary.article_id, "Unknown Title")
                formatted = summary.format_for_display(article_title)
                formatted_summaries.append(formatted)
                
            # Save to file
            success = save_summaries_to_file(formatted_summaries, filename)
            
            if success:
                logger.info(f"Successfully saved summaries to file: {filename}")
            else:
                logger.error(f"Failed to save summaries to file: {filename}")
                
            return success
        except Exception as e:
            error_message = f"Error saving summaries to file: {filename}"
            return error_handler.handle_error(
                e, logger, error_message, raise_error=False, default_return=False
            )

    def run(self) -> Tuple[List[Article], List[Summary]]:
        """
        Run the news fetcher application.

        Returns:
            A tuple containing the list of articles and summaries.
        """
        # Validate configuration
        if not self.validate_config():
            logger.error("Invalid configuration")
            return [], []
            
        # Fetch articles
        articles = self.fetch_articles()
        if not articles:
            logger.warning("No articles fetched")
            return [], []
            
        # Filter articles by themes
        filtered_articles = self.filter_articles(articles, config.THEMES)
        if not filtered_articles:
            logger.warning("No articles match the specified themes")
            return [], []
            
        # Save articles to the database
        saved_articles = self.save_articles_to_db(filtered_articles)
        if not saved_articles:
            logger.warning("No articles saved to the database")
            return [], []
            
        # Summarize articles
        summaries = [self.summarize_article(article) for article in saved_articles]
        
        # Save summaries to the database
        saved_summaries = self.save_summaries_to_db(summaries)
        
        # Save summaries to a file
        self.save_summaries_to_file(saved_summaries, saved_articles, config.OUTPUT_FILE)
        
        return saved_articles, saved_summaries

    def run_async(self) -> asyncio.Future:
        """
        Run the news fetcher application asynchronously.

        Returns:
            A future that resolves to a tuple containing the list of articles and summaries.
        """
        async def _run_async():
            # Validate configuration
            if not self.validate_config():
                logger.error("Invalid configuration")
                return [], []
                
            # Fetch articles
            articles = await self.fetch_articles_async()
            if not articles:
                logger.warning("No articles fetched")
                return [], []
                
            # Filter articles by themes
            filtered_articles = self.filter_articles(articles, config.THEMES)
            if not filtered_articles:
                logger.warning("No articles match the specified themes")
                return [], []
                
            # Save articles to the database
            saved_articles = self.save_articles_to_db(filtered_articles)
            if not saved_articles:
                logger.warning("No articles saved to the database")
                return [], []
                
            # Summarize articles
            summaries = await self.summarize_articles_async(saved_articles)
            
            # Save summaries to the database
            saved_summaries = self.save_summaries_to_db(summaries)
            
            # Save summaries to a file
            self.save_summaries_to_file(saved_summaries, saved_articles, config.OUTPUT_FILE)
            
            return saved_articles, saved_summaries
            
        return asyncio.ensure_future(_run_async())

    def run_background(self) -> int:
        """
        Run the news fetcher application in the background.

        Returns:
            Task ID for the background task.
        """
        return run_in_background(self.run)


# Create a singleton instance for easy import
news_fetcher = NewsFetcher()
