from typing import List, Dict, Any
from datetime import datetime
import json
import os

from src.sentiment.base_analyzer import BaseSentimentAnalyzer, SentimentResult
from src.sentiment.fear_greed_index import FearGreedAnalyzer, CNNFearGreedFetcher
from src.sentiment.reddit_analyzer import RedditSentimentAnalyzer
from src.sentiment.rss_feed import RSSFeedSentimentAnalyzer
from src.const.url import FNG_API_URL

class CombinedSentimentAnalyzer:
    def __init__(self, history_file: str = "sentiment_history.json"):
        self.analyzers: List[BaseSentimentAnalyzer] = [
            FearGreedAnalyzer(CNNFearGreedFetcher(FNG_API_URL)),
            RedditSentimentAnalyzer(),
            RSSFeedSentimentAnalyzer("https://rss.app/feeds/v1.1/t3OljJfE1OVl9TMq.json"),  # CoinTelegraph
            RSSFeedSentimentAnalyzer("https://rss.app/feeds/v1.1/tyEkD8QQJwPnw38P.json")   # CryptoSlate
        ]
        self.analyzer_names = [
            "Fear & Greed Index",
            "Reddit Sentiment",
            "CoinTelegraph RSS",
            "CryptoSlate RSS"
        ]
        self.history_file = history_file
        self.historical_data = self._load_history()
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load historical sentiment data from file"""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_history(self):
        """Save historical sentiment data to file"""
        with open(self.history_file, 'w') as f:
            json.dump(self.historical_data, f, indent=2)
    
    def get_all_sentiments(self) -> List[tuple[str, SentimentResult]]:
        """Get sentiment analysis results from all analyzers"""
        results = []
        timestamp = datetime.now().isoformat()
        
        for name, analyzer in zip(self.analyzer_names, self.analyzers):
            try:
                result = analyzer.get_sentiment()
                if not result.timestamp:
                    result.timestamp = timestamp
                results.append((name, result))
            except Exception as e:
                print(f"Error getting sentiment from {name}: {str(e)}")
        
        return results
    
    def get_aggregate_sentiment(self) -> SentimentResult:
        """Calculate aggregate sentiment from all analyzers"""
        results = self.get_all_sentiments()
        if not results:
            raise ValueError("No sentiment results available")
        
        # Calculate average sentiment value
        total_value = sum(result.value for _, result in results)
        avg_value = total_value / len(results)
        
        # Create aggregate result
        classification = self.analyzers[0].classify_sentiment(avg_value)
        interpretation = f"Aggregate sentiment based on {len(results)} analyzers"
        
        # Store historical data
        historical_entry = {
            "timestamp": datetime.now().isoformat(),
            "fear_greed_value": next((r.value for n, r in results if "Fear & Greed" in n), None),
            "reddit_value": next((r.value for n, r in results if "Reddit" in n), None),
            "cointelegraph_value": next((r.value for n, r in results if "CoinTelegraph" in n), None),
            "cryptoslate_value": next((r.value for n, r in results if "CryptoSlate" in n), None),
            "aggregate_value": avg_value,
            "classification": classification
        }
        self.historical_data.append(historical_entry)
        self._save_history()
        
        return SentimentResult(
            value=avg_value,
            classification=classification,
            interpretation=interpretation,
            timestamp=datetime.now().isoformat(),
            raw_data={"individual_results": [
                {
                    "analyzer": name,
                    "value": r.value,
                    "classification": r.classification,
                    "items_analyzed": r.raw_data.get('items_analyzed'),
                    "latest_item_date": r.raw_data.get('latest_item_date')
                } for name, r in results
            ]}
        )

if __name__ == "__main__":
    from src.combination.sentiment_visualizer import save_analysis_report
    
    analyzer = CombinedSentimentAnalyzer()
    
    # Get individual results
    print("\nIndividual Analyzer Results:")
    results = analyzer.get_all_sentiments()
    for name, result in results:
        print(f"\n{name} Analysis:")
        print(f"Value: {result.value:.2f}")
        print(f"Classification: {result.classification}")
        print(f"Interpretation: {result.interpretation}")
        if result.raw_data.get('items_analyzed'):
            print(f"Items Analyzed: {result.raw_data['items_analyzed']}")
        if result.raw_data.get('latest_item_date'):
            print(f"Latest Item Date: {result.raw_data['latest_item_date']}")
    
    # Get aggregate result
    print("\nAggregate Result:")
    aggregate = analyzer.get_aggregate_sentiment()
    print(f"Value: {aggregate.value:.2f}")
    print(f"Classification: {aggregate.classification}")
    
    # Generate visualization report
    save_analysis_report(results, aggregate, analyzer.historical_data)