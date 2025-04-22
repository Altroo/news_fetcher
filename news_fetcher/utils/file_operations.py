"""
File Operations Utilities

This module provides utility functions for file operations.
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional, Union

# Set up logging
logger = logging.getLogger(__name__)


def save_text_to_file(text: str, filename: str) -> bool:
    """
    Save text to a file.

    Args:
        text: The text to save.
        filename: The name of the file to save to.

    Returns:
        True if the save was successful, False otherwise.
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
            
        logger.info(f"Successfully saved text to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error saving text to {filename}: {str(e)}")
        return False


def save_summaries_to_file(summaries: List[str], filename: str) -> bool:
    """
    Save a list of summaries to a file.

    Args:
        summaries: The list of summaries to save.
        filename: The name of the file to save to.

    Returns:
        True if the save was successful, False otherwise.
    """
    try:
        text = "\n\n".join(summaries)
        return save_text_to_file(text, filename)
    except Exception as e:
        logger.error(f"Error saving summaries to {filename}: {str(e)}")
        return False


def save_json_to_file(data: Union[Dict[str, Any], List[Any]], filename: str) -> bool:
    """
    Save data as JSON to a file.

    Args:
        data: The data to save.
        filename: The name of the file to save to.

    Returns:
        True if the save was successful, False otherwise.
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Successfully saved JSON data to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error saving JSON data to {filename}: {str(e)}")
        return False


def load_text_from_file(filename: str) -> Optional[str]:
    """
    Load text from a file.

    Args:
        filename: The name of the file to load from.

    Returns:
        The text from the file, or None if the file could not be loaded.
    """
    try:
        if not os.path.exists(filename):
            logger.warning(f"File {filename} does not exist")
            return None
            
        with open(filename, "r", encoding="utf-8") as f:
            text = f.read()
            
        logger.info(f"Successfully loaded text from {filename}")
        return text
    except Exception as e:
        logger.error(f"Error loading text from {filename}: {str(e)}")
        return None


def load_json_from_file(filename: str) -> Optional[Union[Dict[str, Any], List[Any]]]:
    """
    Load JSON data from a file.

    Args:
        filename: The name of the file to load from.

    Returns:
        The data from the file, or None if the file could not be loaded.
    """
    try:
        if not os.path.exists(filename):
            logger.warning(f"File {filename} does not exist")
            return None
            
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        logger.info(f"Successfully loaded JSON data from {filename}")
        return data
    except Exception as e:
        logger.error(f"Error loading JSON data from {filename}: {str(e)}")
        return None


def ensure_directory_exists(directory: str) -> bool:
    """
    Ensure that a directory exists, creating it if necessary.

    Args:
        directory: The directory to ensure exists.

    Returns:
        True if the directory exists or was created, False otherwise.
    """
    try:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Ensured directory {directory} exists")
        return True
    except Exception as e:
        logger.error(f"Error ensuring directory {directory} exists: {str(e)}")
        return False


def get_file_extension(filename: str) -> str:
    """
    Get the extension of a file.

    Args:
        filename: The name of the file.

    Returns:
        The extension of the file.
    """
    return os.path.splitext(filename)[1].lower()
