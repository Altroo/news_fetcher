"""
Article Model

This module provides a model for news articles.
"""
from datetime import datetime
from typing import Optional, ClassVar, List, Dict, Any

from news_fetcher.models.base import BaseModel


class Article(BaseModel):
    """Model representing a news article."""

    # Define the fields for the Article model
    fields: ClassVar[List[str]] = [
        "id",
        "source_id",
        "source_name",
        "author",
        "title",
        "description",
        "url",
        "url_to_image",
        "published_at",
        "content",
        "fetched_at",
        "themes"
    ]
    table_name: ClassVar[str] = "articles"

    def __init__(self, id_: Optional[int] = None, source_id: Optional[str] = None, source_name: Optional[str] = None,
                 author: Optional[str] = None, title: Optional[str] = None, description: Optional[str] = None,
                 url: Optional[str] = None, url_to_image: Optional[str] = None, published_at: Optional[datetime] = None,
                 content: Optional[str] = None, fetched_at: Optional[datetime] = None,
                 themes: Optional[List[str]] = None, **kwargs):
        """
        Initialize an Article instance.

        Args:
            id_: The database ID of the article.
            source_id: The ID of the news source.
            source_name: The name of the news source.
            author: The author of the article.
            title: The title of the article.
            description: The description of the article.
            url: The URL of the article.
            url_to_image: The URL of the article's image.
            published_at: The publication date of the article.
            content: The content of the article.
            fetched_at: The date the article was fetched.
            themes: A list of themes associated with the article.
        """
        super().__init__(**kwargs)
        self.id = id_
        self.source_id = source_id
        self.source_name = source_name
        self.author = author
        self.title = title
        self.description = description
        self.url = url
        self.url_to_image = url_to_image
        self.published_at = published_at
        self.content = content
        self.fetched_at = fetched_at or datetime.now()
        self.themes = themes or []

    @classmethod
    def from_api_response(cls, article_data: Dict[str, Any]) -> 'Article':
        """
        Create an Article instance from a News API response.

        Args:
            article_data: The article data from the News API.

        Returns:
            A new Article instance.
        """
        # Extract source information
        source = article_data.get("source", {})
        source_id = source.get("id")
        source_name = source.get("name")

        # Parse the published_at date if it exists
        published_at_str = article_data.get("publishedAt")
        published_at = None
        if published_at_str:
            try:
                published_at = datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                # If parsing fails, use the current time
                published_at = datetime.now()

        return cls(
            source_id=source_id,
            source_name=source_name,
            author=article_data.get("author"),
            title=article_data.get("title"),
            description=article_data.get("description"),
            url=article_data.get("url"),
            url_to_image=article_data.get("urlToImage"),
            published_at=published_at,
            content=article_data.get("content"),
            fetched_at=datetime.now(),
            themes=[]  # Themes will be added later after filtering
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Article instance to a dictionary.

        Returns:
            A dictionary representation of the Article.
        """
        result = super().to_dict()
        
        # Convert datetime objects to ISO format strings
        if result["published_at"]:
            result["published_at"] = result["published_at"].isoformat()
        if result["fetched_at"]:
            result["fetched_at"] = result["fetched_at"].isoformat()
            
        # Convert themes list to comma-separated string for storage
        if result["themes"]:
            result["themes"] = ",".join(result["themes"])
            
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseModel:
        """
        Create an Article instance from a dictionary.

        Args:
            data: A dictionary containing article data.

        Returns:
            A new Article instance.
        """
        # Parse datetime strings
        published_at = data.get("published_at")
        if published_at and isinstance(published_at, str):
            try:
                data["published_at"] = datetime.fromisoformat(published_at)
            except ValueError:
                data["published_at"] = None
                
        fetched_at = data.get("fetched_at")
        if fetched_at and isinstance(fetched_at, str):
            try:
                data["fetched_at"] = datetime.fromisoformat(fetched_at)
            except ValueError:
                data["fetched_at"] = None
                
        # Parse themes string
        themes = data.get("themes")
        if themes and isinstance(themes, str):
            data["themes"] = themes.split(",")
        else:
            data["themes"] = []
            
        return super().from_dict(data)
