"""
Summary Model

This module provides a model for article summaries.
"""
from datetime import datetime
from typing import Optional, ClassVar, List, Dict, Any

from news_fetcher.models.base import BaseModel


class Summary(BaseModel):
    """Model representing an article summary."""

    # Define the fields for the Summary model
    fields: ClassVar[List[str]] = [
        "id",
        "article_id",
        "content",
        "created_at",
        "model_used"
    ]
    table_name: ClassVar[str] = "summaries"

    def __init__(self, id_: Optional[int] = None, article_id: Optional[int] = None, content: Optional[str] = None,
                 created_at: Optional[datetime] = None, model_used: Optional[str] = None, **kwargs):
        """
        Initialize a Summary instance.

        Args:
            id_: The database ID of the summary.
            article_id: The database ID of the associated article.
            content: The summary content.
            created_at: The date the summary was created.
            model_used: The name/ID of the model used to generate the summary.
        """
        super().__init__(**kwargs)
        self.id = id_
        self.article_id = article_id
        self.content = content
        self.created_at = created_at or datetime.now()
        self.model_used = model_used

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Summary instance to a dictionary.

        Returns:
            A dictionary representation of the Summary.
        """
        result = super().to_dict()
        
        # Convert datetime objects to ISO format strings
        if result["created_at"]:
            result["created_at"] = result["created_at"].isoformat()
            
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseModel:
        """
        Create a Summary instance from a dictionary.

        Args:
            data: A dictionary containing summary data.

        Returns:
            A new Summary instance.
        """
        # Parse datetime strings
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            try:
                data["created_at"] = datetime.fromisoformat(created_at)
            except ValueError:
                data["created_at"] = None
                
        return super().from_dict(data)

    def format_for_display(self, article_title: Optional[str] = None) -> str:
        """
        Format the summary for display.

        Args:
            article_title: The title of the associated article.

        Returns:
            A formatted string representation of the summary.
        """
        if article_title:
            return f"Title: {article_title}\nSummary: {self.content}"
        return f"Summary: {self.content}"
