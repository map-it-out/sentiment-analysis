from dataclasses import dataclass
from datetime import datetime
import requests
from typing import List, Optional
import json

@dataclass
class RSSItem:
    """Data class to store RSS feed item information"""
    content_text: str
    title: str
    published_date: Optional[datetime]
    link: str

class RSSFeedError(Exception):
    """Custom exception for RSS feed errors"""
    pass

class RSSFeedScraper:
    """Scrapes and processes RSS feed data"""
    def __init__(self, feed_url: str = "https://rss.app/feeds/v1.1/aBVTZHuR5sM4z6vJ.json"):
        self.feed_url = feed_url

    def fetch_feed(self) -> List[RSSItem]:
        """Fetch and parse RSS feed data"""
        try:
            response = requests.get(self.feed_url)
            response.raise_for_status()
            feed_data = response.json()
            
            return self._parse_items(feed_data.get('items', []))
        except Exception as e:
            raise RSSFeedError(f"Failed to fetch RSS feed: {str(e)}")

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string with multiple format attempts"""
        if not date_str:
            return None
            
        date_formats = [
            '%Y-%m-%dT%H:%M:%S.%fZ',  # Standard ISO format with microseconds
            '%Y-%m-%dT%H:%M:%SZ',     # ISO format without microseconds
            '%Y-%m-%d %H:%M:%S',      # Basic datetime format
            '%Y-%m-%d'                # Just date
        ]
        
        for date_format in date_formats:
            try:
                return datetime.strptime(date_str, date_format)
            except ValueError:
                continue
        return None

    def _parse_items(self, items: List[dict]) -> List[RSSItem]:
        """Parse RSS items into RSSItem objects"""
        parsed_items = []
        for item in items:
            try:
                published_date = self._parse_date(item.get('published_date', ''))
                parsed_items.append(RSSItem(
                    content_text=item.get('content_text', ''),
                    title=item.get('title', ''),
                    published_date=published_date,
                    link=item.get('link', '')
                ))
            except Exception as e:
                print(f"Warning: Failed to parse item: {str(e)}")
                continue
        
        return parsed_items

    def get_content_texts(self) -> List[str]:
        """Get only the content_text from all RSS items"""
        items = self.fetch_feed()
        return [item.content_text for item in items]

# Example usage
if __name__ == "__main__":
    scraper = RSSFeedScraper()
    try:
        items = scraper.fetch_feed()
        print(f"Found {len(items)} items in the RSS feed:")
        for item in items:
            print("\nTitle:", item.title)
            print("Content:", item.content_text[:200] + "..." if len(item.content_text) > 200 else item.content_text)
            print("Published:", item.published_date)
            print("Link:", item.link)
    except RSSFeedError as e:
        print(f"Error: {e}")