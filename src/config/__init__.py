"""Configuration management for the sentiment analysis system"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

@dataclass
class APIConfig:
    """API configuration settings"""
    fng_api_url: str
    bitcoin_price_api_url: str = "https://api.alternative.me/v2/ticker/?limit=1"
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_user_agent: Optional[str] = None
    spreadsheet_id: Optional[str] = None
    reddit_rss_feed_url: str = "https://www.reddit.com/r/wallstreetbets/.rss"
    rss_base_url: str = "https://rss.app/feeds/v1.1"
    rss_feeds: dict = None  # Will be populated in _load_config

@dataclass
class SentimentConfig:
    """Sentiment analysis configuration"""
    fear_greed_weight: float = 0.25
    reddit_weight: float = 0.25
    rss_weight: float = 0.25
    rss_2_weight: float = 0.25
    reddit_post_limit: int = 100
    reddit_default_subreddit: str = "CryptoCurrency"
    reddit_default_sort: str = "new"    

class Config:
    """Global configuration singleton"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Load configuration from environment variables"""
        load_dotenv()
        
        self.api_config = APIConfig(
            fng_api_url="https://api.alternative.me/fng/",
            reddit_client_id=os.getenv('REDDIT_CLIENT_ID'),
            reddit_client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            reddit_user_agent=os.getenv('REDDIT_USER_AGENT'),
            spreadsheet_id=os.getenv('SPREADSHEET_ID')
        )
        
        # Load RSS feed configuration
        self.api_config.rss_feeds = {
            "CoinTelegraph": f"{self.api_config.rss_base_url}/{os.getenv('COIN_TELEGRAPH_RSS_ID')}.json",
            "CryptoSlate": f"{self.api_config.rss_base_url}/{os.getenv('CRYPTO_SLATE_RSS_ID')}.json"
        }
        
        self.sentiment = SentimentConfig()

# Global config instance
config = Config()
