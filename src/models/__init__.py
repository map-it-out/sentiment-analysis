"""Data models for the sentiment analysis system"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

@dataclass
class SentimentScore:
    """Base class for sentiment scores"""
    value: float  # Normalized value between -1 and 1
    raw_value: float  # Original value before normalization
    timestamp: datetime
    
    @property
    def normalized_score(self) -> float:
        """Convert score from [-1, 1] to [0, 1] range"""
        return (self.value + 1) / 2

@dataclass
class FearGreedScore(SentimentScore):
    """Fear and Greed index score"""
    classification: str
    interpretation: str

@dataclass
class RedditScore(SentimentScore):
    """Reddit sentiment score"""
    positive_ratio: float
    negative_ratio: float
    neutral_ratio: float
    post_count: int
    
@dataclass
class PriceData:
    """Cryptocurrency price data"""
    current_price: float
    price_1h: float
    price_24h: float
    change_1h: float
    change_24h: float
    timestamp: datetime

@dataclass
class CombinedSentiment:
    """Combined sentiment analysis result"""
    fear_greed_score: FearGreedScore
    reddit_score: RedditScore
    price_data: Optional[PriceData]
    weighted_fear_greed: float
    weighted_reddit: float
    final_score: float
    timestamp: datetime
    
    def to_sheet_row(self) -> list:
        """Convert to Google Sheets row format"""
        return [
            self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            self.fear_greed_score.normalized_score,
            self.reddit_score.normalized_score,
            self.weighted_fear_greed,
            self.weighted_reddit,
            self.final_score,
            self.price_data.current_price if self.price_data else None,
            self.price_data.price_1h if self.price_data else None,
            f"{self.price_data.change_1h:.2%}" if self.price_data else None,
            self.price_data.price_24h if self.price_data else None,
            f"{self.price_data.change_24h:.2%}" if self.price_data else None
        ]
