"""
A basic adapter that all adapters should inherit from.

Provides abstract methods that all adapters should implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from _types.feed_types import Feed

class BaseAdapter:
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_feed(self) -> Feed:
        """
        Fetch the feed and parse it into a Feed object.

        Returns:
            Feed: The parsed feed.
        """
        pass