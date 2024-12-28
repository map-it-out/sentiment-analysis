from dataclasses import dataclass
from datetime import datetime
import requests
from typing import List, Optional, Dict, Any
import json
from nltk.sentiment import SentimentIntensityAnalyzer
from src.sentiment.base_analyzer import BaseSentimentAnalyzer, SentimentResult
from src.const.url import RSS_FEED_URL

@dataclass
class RSSItem:
    """Data class to store RSS feed item information"""
    id: str
    url: str
    title: str
    content_text: str
    content_html: str
    image: Optional[str]
    published_date: Optional[datetime]
    authors: List[Dict[str, str]]
    attachments: List[Dict[str, str]]

class RSSFeedError(Exception):
    """Custom exception for RSS feed errors"""
    pass

class RSSFeedScraper:
    """Scrapes and processes RSS feed data"""
    def __init__(self, feed_url: str = RSS_FEED_URL):
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
            published_date = self._parse_date(item.get('date_published'))
            parsed_items.append(
                RSSItem(
                    id=item.get('id', ''),
                    url=item.get('url', ''),
                    title=item.get('title', ''),
                    content_text=item.get('content_text', ''),
                    content_html=item.get('content_html', ''),
                    image=item.get('image'),
                    published_date=published_date,
                    authors=item.get('authors', []),
                    attachments=item.get('attachments', [])
                )
            )
        return parsed_items

    def get_content_texts(self) -> List[str]:
        """Get only the content_text from all RSS items"""
        items = self.fetch_feed()
        return [item.content_text for item in items]

class RSSFeedSentimentAnalyzer(BaseSentimentAnalyzer):
    """Analyzes sentiment from RSS feed content"""
    def __init__(self, feed_url: str = RSS_FEED_URL):
        self.scraper = RSSFeedScraper(feed_url)
        self.sia = SentimentIntensityAnalyzer()
    
    def get_sentiment(self) -> SentimentResult:
        """Get sentiment analysis from RSS feed items"""
        try:
            # Fetch RSS items
            items = self.scraper.fetch_feed()
            
            if not items:
                return SentimentResult(
                    value=0.0,
                    classification="Neutral",
                    interpretation="No RSS items found",
                    raw_data={"items_analyzed": 0},
                    timestamp=datetime.now().isoformat()
                )
            
            # Calculate sentiment for each item
            sentiments = []
            for item in items:
                # Analyze both title and content
                title_scores = self.sia.polarity_scores(item.title)
                content_scores = self.sia.polarity_scores(item.content_text)
                
                # Average the compound scores (giving more weight to title)
                item_sentiment = (title_scores['compound'] * 0.6 + 
                                content_scores['compound'] * 0.4)
                sentiments.append(item_sentiment)
            
            # Calculate average sentiment
            avg_sentiment = sum(sentiments) / len(sentiments)
            
            # Get classification based on normalized score
            classification = self.classify_sentiment(avg_sentiment)
            
            # Create interpretation
            interpretation = f"{classification} - RSS feed sentiment is "
            if avg_sentiment > 0:
                interpretation += "positive, showing optimistic market signals"
            elif avg_sentiment < 0:
                interpretation += "negative, showing pessimistic market signals"
            else:
                interpretation += "neutral, showing balanced market signals"
            
            return SentimentResult(
                value=avg_sentiment,
                classification=classification,
                interpretation=interpretation,
                raw_data={
                    "items_analyzed": len(items),
                    "latest_item_date": items[0].published_date.isoformat() if items[0].published_date else None
                },
                timestamp=datetime.now().isoformat()
            )
            
        except RSSFeedError as e:
            return SentimentResult(
                value=0.0,
                classification="Error",
                interpretation=f"Failed to analyze RSS feed: {str(e)}",
                raw_data={"error": str(e)},
                timestamp=datetime.now().isoformat()
            )

# Example usage
if __name__ == "__main__":
    analyzer = RSSFeedSentimentAnalyzer("https://rss.app/feeds/v1.1/t3OljJfE1OVl9TMq.json")
    try:
        sentiment = analyzer.get_sentiment()
        print(f"RSS Feed Sentiment Analysis:")
        print(f"Value: {sentiment.value:.2f}")
        print(f"Classification: {sentiment.classification}")
        print(f"Interpretation: {sentiment.interpretation}")
        print(f"Items Analyzed: {sentiment.raw_data['items_analyzed']}")
        if sentiment.raw_data.get('latest_item_date'):
            print(f"Latest Item Date: {sentiment.raw_data['latest_item_date']}")
    except Exception as e:
        print(f"Error: {e}")