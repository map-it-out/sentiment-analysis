from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class SentimentResult:
    value: float  # normalized value between -1 and 1
    classification: str  # e.g., "Fear", "Greed", "Neutral"
    interpretation: str
    raw_data: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None

class BaseSentimentAnalyzer(ABC):
    @abstractmethod
    def get_sentiment(self) -> SentimentResult:
        """Get sentiment analysis result"""
        pass

    def normalize_score(self, value: float, old_min: float, old_max: float) -> float:
        """Normalize any score to range [-1, 1]"""
        return 2 * ((value - old_min) / (old_max - old_min)) - 1

    def classify_sentiment(self, value: float) -> str:
        """Classify normalized sentiment value"""
        if value < -0.6:
            return "Extreme Fear"
        elif value < -0.2:
            return "Fear"
        elif value < 0.2:
            return "Neutral"
        elif value < 0.6:
            return "Greed"
        else:
            return "Extreme Greed"
