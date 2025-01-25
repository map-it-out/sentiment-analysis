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

@dataclass
class SentimentConfig:
    """Sentiment analysis configuration"""
    fear_greed_weight: float = 0.5
    reddit_weight: float = 0.5
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
        
        self.api = APIConfig(
            fng_api_url=os.getenv('FNG_API_URL', 'https://api.alternative.me/fng/'),
            reddit_client_id=os.getenv('REDDIT_CLIENT_ID'),
            reddit_client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            reddit_user_agent=os.getenv('REDDIT_USER_AGENT'),
            spreadsheet_id=os.getenv('SPREADSHEET_ID')
        )
        
        self.sentiment = SentimentConfig()

# Global config instance
config = Config()
