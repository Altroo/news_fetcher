"""
Repository Module

This module provides repository classes for database operations on specific models.
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from news_fetcher.db.database import db
from news_fetcher.models.article import Article
from news_fetcher.models.summary import Summary

# Set up logging
logger = logging.getLogger(__name__)


class ArticleRepository:
    """Repository for Article model operations."""

    @staticmethod
    def save(article: Article) -> Article:
        """
        Save an article to the database.

        Args:
            article: The article to save.

        Returns:
            The saved article with ID.
        """
        try:
            if article.id:
                db.update(article)
            else:
                article.id = db.insert(article)
            return article
        except Exception as e:
            logger.error(f"Error saving article: {str(e)}")
            raise

    @staticmethod
    def get_by_id(article_id: int) -> Optional[Article]:
        """
        Get an article by ID.

        Args:
            article_id: The ID of the article.

        Returns:
            The article if found, None otherwise.
        """
        try:
            return db.get_by_id(Article, article_id)
        except Exception as e:
            logger.error(f"Error getting article by ID: {str(e)}")
            raise

    @staticmethod
    def get_all(limit: int = 100, offset: int = 0) -> List[Article]:
        """
        Get all articles with pagination.

        Args:
            limit: The maximum number of articles to retrieve.
            offset: The number of articles to skip.

        Returns:
            A list of articles.
        """
        try:
            return db.get_all(Article, limit, offset)
        except Exception as e:
            logger.error(f"Error getting all articles: {str(e)}")
            raise

    @staticmethod
    def delete(article: Article) -> bool:
        """
        Delete an article.

        Args:
            article: The article to delete.

        Returns:
            True if the deletion was successful, False otherwise.
        """
        try:
            return db.delete(article)
        except Exception as e:
            logger.error(f"Error deleting article: {str(e)}")
            raise

    @staticmethod
    def filter_by_themes(themes: List[str], limit: int = 100, offset: int = 0) -> List[Article]:
        """
        Filter articles by themes.

        Args:
            themes: The themes to filter by.
            limit: The maximum number of articles to retrieve.
            offset: The number of articles to skip.

        Returns:
            A list of articles matching the themes.
        """
        try:
            # Construct a SQL query to filter by themes
            # This is a simple implementation that checks if any theme is in the themes column
            theme_conditions = []
            params = []
            
            for theme in themes:
                theme_conditions.append("themes LIKE ?")
                params.append(f"%{theme}%")
                
            if not theme_conditions:
                return []
                
            where_clause = " OR ".join(theme_conditions)
            sql = f"SELECT * FROM {Article.table_name} WHERE {where_clause} LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            return db.query(Article, sql, tuple(params))
        except Exception as e:
            logger.error(f"Error filtering articles by themes: {str(e)}")
            raise

    @staticmethod
    def get_by_url(url: str) -> Optional[Article]:
        """
        Get an article by URL.

        Args:
            url: The URL of the article.

        Returns:
            The article if found, None otherwise.
        """
        try:
            sql = f"SELECT * FROM {Article.table_name} WHERE url = ?"
            results = db.query(Article, sql, (url,))
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Error getting article by URL: {str(e)}")
            raise


class SummaryRepository:
    """Repository for Summary model operations."""

    @staticmethod
    def save(summary: Summary) -> Summary:
        """
        Save a summary to the database.

        Args:
            summary: The summary to save.

        Returns:
            The saved summary with ID.
        """
        try:
            if summary.id:
                db.update(summary)
            else:
                summary.id = db.insert(summary)
            return summary
        except Exception as e:
            logger.error(f"Error saving summary: {str(e)}")
            raise

    @staticmethod
    def get_by_id(summary_id: int) -> Optional[Summary]:
        """
        Get a summary by ID.

        Args:
            summary_id: The ID of the summary.

        Returns:
            The summary if found, None otherwise.
        """
        try:
            return db.get_by_id(Summary, summary_id)
        except Exception as e:
            logger.error(f"Error getting summary by ID: {str(e)}")
            raise

    @staticmethod
    def get_all(limit: int = 100, offset: int = 0) -> List[Summary]:
        """
        Get all summaries with pagination.

        Args:
            limit: The maximum number of summaries to retrieve.
            offset: The number of summaries to skip.

        Returns:
            A list of summaries.
        """
        try:
            return db.get_all(Summary, limit, offset)
        except Exception as e:
            logger.error(f"Error getting all summaries: {str(e)}")
            raise

    @staticmethod
    def delete(summary: Summary) -> bool:
        """
        Delete a summary.

        Args:
            summary: The summary to delete.

        Returns:
            True if the deletion was successful, False otherwise.
        """
        try:
            return db.delete(summary)
        except Exception as e:
            logger.error(f"Error deleting summary: {str(e)}")
            raise

    @staticmethod
    def get_by_article_id(article_id: int) -> List[Summary]:
        """
        Get summaries by article ID.

        Args:
            article_id: The ID of the article.

        Returns:
            A list of summaries for the article.
        """
        try:
            sql = f"SELECT * FROM {Summary.table_name} WHERE article_id = ? ORDER BY created_at DESC"
            return db.query(Summary, sql, (article_id,))
        except Exception as e:
            logger.error(f"Error getting summaries by article ID: {str(e)}")
            raise

    @staticmethod
    def get_latest_summaries(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the latest summaries with article information.

        Args:
            limit: The maximum number of summaries to retrieve.

        Returns:
            A list of dictionaries containing summary and article information.
        """
        try:
            sql = f"""
            SELECT s.*, a.title as article_title, a.url as article_url
            FROM {Summary.table_name} s
            JOIN {Article.table_name} a ON s.article_id = a.id
            ORDER BY s.created_at DESC
            LIMIT ?
            """
            
            cursor = db.execute(sql, (limit,))
            results = []
            
            for row in cursor.fetchall():
                row_dict = dict(row)
                summary = Summary.from_dict(row_dict)
                results.append({
                    "summary": summary,
                    "article_title": row_dict.get("article_title"),
                    "article_url": row_dict.get("article_url")
                })
                
            return results
        except Exception as e:
            logger.error(f"Error getting latest summaries: {str(e)}")
            raise
