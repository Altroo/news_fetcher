"""
Text Processing Utilities

This module provides utility functions for text processing.
"""
import re
import logging
from typing import List, Dict, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)


def filter_articles_by_theme(articles: List[Dict[str, Any]], themes: List[str]) -> List[Dict[str, Any]]:
    """
    Filter articles by themes.

    Args:
        articles: List of article dictionaries.
        themes: List of themes to filter by.

    Returns:
        Filtered list of articles.
    """
    if not themes:
        logger.warning("No themes provided for filtering")
        return articles

    filtered = []
    for article in articles:
        title = article.get("title", "").lower()
        description = article.get("description", "").lower()
        content = article.get("content", "").lower()

        for theme in themes:
            theme_lower = theme.lower()
            if (theme_lower in title or
                    theme_lower in description or
                    theme_lower in content):
                # Add the matching theme to the article for later use
                if "matched_themes" not in article:
                    article["matched_themes"] = []
                article["matched_themes"].append(theme)
                filtered.append(article)
                break

    logger.info(f"Filtered {len(filtered)} articles out of {len(articles)} by themes: {', '.join(themes)}")
    return filtered


def extract_themes_from_text(text: str, candidate_themes: List[str]) -> List[str]:
    """
    Extract themes from text.

    Args:
        text: The text to extract themes from.
        candidate_themes: List of candidate themes to look for.

    Returns:
        List of themes found in the text.
    """
    if not text or not candidate_themes:
        return []

    text_lower = text.lower()
    found_themes = []

    for theme in candidate_themes:
        theme_lower = theme.lower()
        if theme_lower in text_lower:
            found_themes.append(theme)

    return found_themes


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace, HTML tags, etc.

    Args:
        text: The text to clean.

    Returns:
        Cleaned text.
    """
    if not text:
        return ""

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


def truncate_text(text: str, max_length: int = 100, add_ellipsis: bool = True) -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: The text to truncate.
        max_length: Maximum length of the truncated text.
        add_ellipsis: Whether to add an ellipsis at the end of truncated text.

    Returns:
        Truncated text.
    """
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    truncated = text[:max_length].rstrip()

    if add_ellipsis:
        truncated += "..."

    return truncated


def get_article_text(article: Dict[str, Any]) -> str:
    """
    Get the text content of an article.

    Args:
        article: Article dictionary.

    Returns:
        Text content of the article.
    """
    # Prefer full content if available; otherwise, use the description
    content = article.get("content") or article.get("description") or ""
    return clean_text(content)


def format_summary(article_title: str, summary_text: str) -> str:
    """
    Format a summary for display.

    Args:
        article_title: The title of the article.
        summary_text: The summary text.

    Returns:
        Formatted summary.
    """
    return f"Title: {article_title}\nSummary: {summary_text}"
