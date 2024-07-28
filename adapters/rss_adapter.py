import feedparser

from .base_adapter import BaseAdapter
from _types.feed_types import Feed, Entry
from database import DatabaseManager

class RSSAdapter(BaseAdapter):
    """
    Adapter to fetch and parse RSS feeds.
    
    Attributes:
        url (str): The URL of the RSS feed.
    """
    def __init__(self, url: str):
        self.url = url
        self.db_manager = DatabaseManager()

    def get_feed(self):
        """
        Fetch the RSS feed and parse it into a Feed object.
        
        Returns:
            Feed: The parsed feed.
        """
        rss_feed = feedparser.parse(self.url)
        feed = Feed(rss_feed.feed.title)
        for entry in rss_feed.entries[:5]:  # Process only the first 5 entries for brevity
            title = entry.title
            text = entry.summary
            image = entry.media_content[0]['url'] if 'media_content' in entry else None
            url = entry.link
            feed.add_entry(Entry(title, text, image, url))
        self.db_manager.save_feed(feed)
        return feed