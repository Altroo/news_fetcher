"""
Asynchronous Utilities

This module provides utilities for asynchronous processing.
"""
import asyncio
import logging
import threading
from typing import List, Dict, Any, Optional, Callable, Awaitable, TypeVar, Generic, Union
from concurrent.futures import ThreadPoolExecutor

import aiohttp

from news_fetcher.utils.logging_config import get_logger

# Set up logging
logger = get_logger("async_utils")

# Type variables
T = TypeVar('T')
R = TypeVar('R')


class AsyncRequestClient:
    """Client for making asynchronous HTTP requests."""

    def __init__(self, timeout: int = 30, max_concurrent_requests: int = 10):
        """
        Initialize the async request client.

        Args:
            timeout: Request timeout in seconds.
            max_concurrent_requests: Maximum number of concurrent requests.
        """
        self.timeout = timeout
        self.max_concurrent_requests = max_concurrent_requests
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.session = None

    async def __aenter__(self):
        """
        Enter the async context manager.

        Returns:
            The client instance.
        """
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the async context manager.

        Args:
            exc_type: Exception type.
            exc_val: Exception value.
            exc_tb: Exception traceback.
        """
        if self.session:
            await self.session.close()

    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make an asynchronous GET request.

        Args:
            url: The URL to request.
            params: Query parameters.
            headers: HTTP headers.

        Returns:
            The JSON response.

        Raises:
            aiohttp.ClientError: If the request fails.
        """
        async with self.semaphore:
            async with self.session.get(url, params=params, headers=headers) as response:
                response.raise_for_status()
                return await response.json()

    async def post(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make an asynchronous POST request.

        Args:
            url: The URL to request.
            json: JSON data to send.
            headers: HTTP headers.

        Returns:
            The JSON response.

        Raises:
            aiohttp.ClientError: If the request fails.
        """
        async with self.semaphore:
            async with self.session.post(url, json=json, headers=headers) as response:
                response.raise_for_status()
                return await response.json()

    @staticmethod
    async def gather_with_concurrency(
        concurrency: int,
        *tasks: Awaitable[T]
    ) -> List[T]:
        """
        Run tasks with a concurrency limit.

        Args:
            concurrency: Maximum number of concurrent tasks.
            *tasks: Tasks to run.

        Returns:
            List of task results.
        """
        semaphore = asyncio.Semaphore(concurrency)

        async def sem_task(task):
            async with semaphore:
                return await task

        return await asyncio.gather(*(sem_task(task) for task in tasks))


class BackgroundTaskProcessor:
    """Processor for running tasks in the background."""

    def __init__(self, max_workers: int = 5):
        """
        Initialize the background task processor.

        Args:
            max_workers: Maximum number of worker threads.
        """
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks = {}
        self.task_counter = 0
        self.lock = threading.Lock()

    def submit_task(
        self,
        func: Callable[..., R],
        *args,
        **kwargs
    ) -> int:
        """
        Submit a task to be executed in the background.

        Args:
            func: The function to execute.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            A task ID that can be used to check the status or get the result.
        """
        with self.lock:
            task_id = self.task_counter
            self.task_counter += 1
            
        future = self.executor.submit(func, *args, **kwargs)
        
        self.tasks[task_id] = {
            "future": future,
            "status": "running",
            "result": None,
            "error": None
        }
        
        future.add_done_callback(lambda f: self._task_done_callback(task_id, f))
        
        logger.info(f"Submitted task {task_id}")
        return task_id

    def _task_done_callback(self, task_id: int, future):
        """
        Callback for when a task is done.

        Args:
            task_id: The ID of the task.
            future: The future object.
        """
        try:
            result = future.result()
            self.tasks[task_id]["result"] = result
            self.tasks[task_id]["status"] = "completed"
            logger.info(f"Task {task_id} completed successfully")
        except Exception as e:
            self.tasks[task_id]["error"] = str(e)
            self.tasks[task_id]["status"] = "failed"
            logger.error(f"Task {task_id} failed: {str(e)}")

    def get_task_status(self, task_id: int) -> Dict[str, Any]:
        """
        Get the status of a task.

        Args:
            task_id: The ID of the task.

        Returns:
            A dictionary with the task status.

        Raises:
            KeyError: If the task ID is not found.
        """
        if task_id not in self.tasks:
            raise KeyError(f"Task {task_id} not found")
            
        task = self.tasks[task_id]
        return {
            "task_id": task_id,
            "status": task["status"],
            "result": task["result"] if task["status"] == "completed" else None,
            "error": task["error"] if task["status"] == "failed" else None
        }

    def wait_for_task(self, task_id: int, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Wait for a task to complete.

        Args:
            task_id: The ID of the task.
            timeout: Maximum time to wait in seconds. If None, wait indefinitely.

        Returns:
            A dictionary with the task status.

        Raises:
            KeyError: If the task ID is not found.
            TimeoutError: If the task does not complete within the timeout.
        """
        if task_id not in self.tasks:
            raise KeyError(f"Task {task_id} not found")
            
        future = self.tasks[task_id]["future"]
        
        try:
            future.result(timeout=timeout)
        except TimeoutError:
            raise TimeoutError(f"Task {task_id} did not complete within the timeout")
            
        return self.get_task_status(task_id)

    def shutdown(self, wait: bool = True):
        """
        Shutdown the executor.

        Args:
            wait: Whether to wait for pending tasks to complete.
        """
        self.executor.shutdown(wait=wait)
        logger.info("Background task processor shut down")


# Create singleton instances for easy import
background_processor = BackgroundTaskProcessor()


async def run_async_tasks(
    tasks: List[Callable[[], Awaitable[T]]],
    concurrency: int = 5
) -> List[T]:
    """
    Run a list of async tasks with a concurrency limit.

    Args:
        tasks: List of async task functions.
        concurrency: Maximum number of concurrent tasks.

    Returns:
        List of task results.
    """
    async with AsyncRequestClient(max_concurrent_requests=concurrency) as client:
        return await client.gather_with_concurrency(concurrency, *(task() for task in tasks))


def run_in_background(
    func: Callable[..., R],
    *args,
    **kwargs
) -> int:
    """
    Run a function in the background.

    Args:
        func: The function to run.
        *args: Positional arguments for the function.
        **kwargs: Keyword arguments for the function.

    Returns:
        A task ID that can be used to check the status or get the result.
    """
    return background_processor.submit_task(func, *args, **kwargs)


def get_background_task_status(task_id: int) -> Dict[str, Any]:
    """
    Get the status of a background task.

    Args:
        task_id: The ID of the task.

    Returns:
        A dictionary with the task status.
    """
    return background_processor.get_task_status(task_id)


def wait_for_background_task(task_id: int, timeout: Optional[float] = None) -> Dict[str, Any]:
    """
    Wait for a background task to complete.

    Args:
        task_id: The ID of the task.
        timeout: Maximum time to wait in seconds. If None, wait indefinitely.

    Returns:
        A dictionary with the task status.
    """
    return background_processor.wait_for_task(task_id, timeout)
