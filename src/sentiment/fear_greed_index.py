from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
import requests
from src.config import config
from src.sentiment.base_analyzer import BaseSentimentAnalyzer, SentimentResult
from src.utils.errors.exceptions import FearGreedFetchError

class FearGreedFetcher(ABC):
    """Abstract base class for fear and greed data fetching"""
    @abstractmethod
    def fetch_data(self, timeout: Optional[float] = None) -> SentimentResult:
        """Fetch fear and greed data"""
        pass

class CNNFearGreedFetcher(FearGreedFetcher):
    """Fetches fear and greed data from CNN's API"""
    def __init__(self, api_url: str = config.api_config.fng_api_url):
        self.api_url = api_url
        
    def _get_interpretation(self, classification: str) -> str:
        """Interpret the fear and greed classification"""
        if classification == "Extreme Greed":
            return "Market might be due for a correction"
        elif classification == "Greed":
            return "Market is optimistic"
        elif classification == "Fear":
            return "Market is pessimistic"
        else:
            return "Might be a buying opportunity"
            
    def fetch_data(self, timeout: Optional[float] = None) -> SentimentResult:
        try:
            response = requests.get(self.api_url, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            
            # Extract the latest data point
            latest = data['data'][0]
            # Convert value from [0, 100] to [-1, 1]
            normalized_value = (float(latest['value']) / 50.0) - 1.0
            
            # Convert Unix timestamp to ISO format
            timestamp = datetime.fromtimestamp(int(latest['timestamp'])).isoformat()
            
            return SentimentResult(
                value=normalized_value,
                classification=latest['value_classification'],
                interpretation=self._get_interpretation(latest['value_classification']),
                raw_data={'original_value': float(latest['value'])},
                timestamp=timestamp
            )
        except Exception as e:
            raise FearGreedFetchError(f"Failed to fetch fear and greed data: {str(e)}")

class FearGreedAnalyzer(BaseSentimentAnalyzer):
    """Analyzes fear and greed data using the base analyzer framework"""
    def __init__(self, fetcher: FearGreedFetcher):
        self.fetcher = fetcher
    
    def get_sentiment(self) -> SentimentResult:
        """Get sentiment analysis result"""
        try:
            return self.fetcher.fetch_data()
        except FearGreedFetchError as e:
            raise e
