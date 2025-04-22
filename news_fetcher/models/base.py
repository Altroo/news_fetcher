"""
Base Model

This module provides a base class for data models.
"""
from datetime import datetime
from typing import Any, Dict, Optional, List, Type, TypeVar, ClassVar

T = TypeVar('T', bound='BaseModel')


class BaseModel:
    """Base class for data models."""

    # Class variables to be overridden by subclasses
    fields: ClassVar[List[str]] = []
    table_name: ClassVar[str] = ""

    def __init__(self, **kwargs):
        """
        Initialize a model instance with the given attributes.

        Args:
            **kwargs: Attribute values to set on the instance.
        """
        for field in self.fields:
            setattr(self, field, kwargs.get(field))

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the model instance to a dictionary.

        Returns:
            A dictionary representation of the model.
        """
        return {field: getattr(self, field) for field in self.fields}

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Create a model instance from a dictionary.

        Args:
            data: A dictionary containing attribute values.

        Returns:
            A new model instance.
        """
        return cls(**{field: data.get(field) for field in cls.fields})

    def __str__(self) -> str:
        """
        Get a string representation of the model.

        Returns:
            A string representation of the model.
        """
        attrs = ", ".join(f"{field}={getattr(self, field)}" for field in self.fields)
        return f"{self.__class__.__name__}({attrs})"

    def __repr__(self) -> str:
        """
        Get a string representation of the model for debugging.

        Returns:
            A string representation of the model.
        """
        return self.__str__()
