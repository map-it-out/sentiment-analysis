from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import requests
from src.config import config
from src.sentiment.base_analyzer import BaseSentimentAnalyzer, SentimentResult

@dataclass
class FearGreedData:
    """Data class to store fear and greed information"""
    value: float
    value_classification: str
    timestamp: datetime
    
class FearGreedFetcher(ABC):
    """Abstract base class for fear and greed data fetching"""
    @abstractmethod
    def fetch_data(self) -> FearGreedData:
        """Fetch fear and greed data"""
        pass

class CNNFearGreedFetcher(FearGreedFetcher):
    """Implementation of fear and greed fetcher using CNN's API"""
    def __init__(self, api_url: str = config.api_config.fng_api_url):
        self.api_url = api_url
        
    def fetch_data(self) -> FearGreedData:
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()
            data = response.json()
            
            # Extract the latest data point
            latest = data['data'][0]
            return FearGreedData(
                value=float(latest['value']),
                value_classification=latest['value_classification'],
                timestamp=datetime.fromtimestamp(int(latest['timestamp']))
            )
        except Exception as e:
            raise FearGreedFetchError(f"Failed to fetch fear and greed data: {str(e)}")

class FearGreedFetchError(Exception):
    """Custom exception for fear and greed fetching errors"""
    pass

class FearGreedAnalyzer(BaseSentimentAnalyzer):
    """Analyzes fear and greed data using the base analyzer framework"""
    def __init__(self, fetcher: FearGreedFetcher):
        self.fetcher = fetcher
    
    def get_sentiment(self) -> SentimentResult:
        """Get sentiment analysis result"""
        try:
            data = self.fetcher.fetch_data()
            # Normalize value from [0, 100] to [-1, 1]
            normalized_value = self.normalize_score(data.value, 0, 100)
            classification = self.classify_sentiment(normalized_value)
            
            return SentimentResult(
                value=normalized_value,
                classification=classification,
                interpretation=self._interpret_value(data.value),
                raw_data={
                    'original_value': data.value,
                    'original_classification': data.value_classification
                },
                timestamp=data.timestamp.isoformat()
            )
        except FearGreedFetchError as e:
            raise e
    
    def _interpret_value(self, value: float) -> str:
        """Interpret the fear and greed value"""
        if value >= 75:
            return "Extreme Greed - Market might be due for a correction"
        elif value >= 50:
            return "Greed - Market is optimistic"
        elif value >= 25:
            return "Fear - Market is pessimistic"
        else:
            return "Extreme Fear - Might be a buying opportunity"

# Example usage
if __name__ == "__main__":
    fetcher = CNNFearGreedFetcher(config.api_config.fng_api_url)
    analyzer = FearGreedAnalyzer(fetcher)
    
    try:
        sentiment = analyzer.get_sentiment()
        print(f"Current Fear & Greed Index: {sentiment.value}")
        print(f"Classification: {sentiment.classification}")
        print(f"Interpretation: {sentiment.interpretation}")
        print(f"Timestamp: {sentiment.timestamp}")
    except FearGreedFetchError as e:
        print(f"Error: {e}")