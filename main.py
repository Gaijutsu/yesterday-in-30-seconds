from adapters import BaseAdapter, RSSAdapter
from database import DatabaseManager
import os
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv()
    rss_adapter = RSSAdapter("https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml")
    feed = rss_adapter.get_feed()
    db_manager = DatabaseManager()
    videos = db_manager.get_entries()
    for video_path in video_paths:
        print(video_path)