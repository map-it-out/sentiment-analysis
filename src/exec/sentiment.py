from datetime import datetime
from pytz import timezone

from src.config import config
from src.models import CombinedSentiment, FearGreedScore, RedditScore
from src.sentiment.fear_greed_index import CNNFearGreedFetcher, FearGreedAnalyzer
from src.sentiment.reddit_analyzer import RedditSentimentAnalyzer
from src.sentiment.rss_feed import RSSFeedSentimentAnalyzer
from src.utils.sheets.sheets_writer import append_to_sheet
from src.services.price_service import price_service
from src.utils.errors.exceptions import SentimentAnalysisError

def collect_and_append_sentiment():
    """Collect all sentiment scores and append them to Google Sheets"""
    try:
        # Initialize analyzers
        fear_greed_fetcher = CNNFearGreedFetcher(config.api_config.fng_api_url)
        fear_greed_analyzer = FearGreedAnalyzer(fear_greed_fetcher)
        reddit_analyzer = RedditSentimentAnalyzer()
        cointelegraph_analyzer = RSSFeedSentimentAnalyzer(config.api_config.rss_feeds["CoinTelegraph"])
        cryptoslate_analyzer = RSSFeedSentimentAnalyzer(config.api_config.rss_feeds["CryptoSlate"])
        
        # Get Fear & Greed sentiment
        fear_greed_result = fear_greed_analyzer.get_sentiment()
        fear_greed_score = FearGreedScore(
            value=fear_greed_result.value,
            raw_value=fear_greed_result.raw_data['original_value'],
            timestamp=datetime.fromisoformat(fear_greed_result.timestamp),
            classification=fear_greed_result.classification,
            interpretation=fear_greed_result.interpretation
        )
        
        # Get Reddit sentiment
        reddit_result = reddit_analyzer.get_sentiment()
        sentiment_dist = reddit_result.raw_data['sentiment_distribution']
        total_posts = reddit_result.raw_data['total_posts']
        reddit_score = RedditScore(
            value=reddit_result.value,
            raw_value=reddit_result.raw_data['average_sentiment'],
            timestamp=datetime.fromisoformat(reddit_result.timestamp),
            positive_ratio=sentiment_dist.get('Positive', 0) / total_posts if total_posts > 0 else 0,
            negative_ratio=sentiment_dist.get('Negative', 0) / total_posts if total_posts > 0 else 0,
            neutral_ratio=sentiment_dist.get('Neutral', 0) / total_posts if total_posts > 0 else 0,
            post_count=total_posts
        )
        
        # Get RSS Feed sentiment
        rss_1_score = cointelegraph_analyzer.get_sentiment()
        rss_2_score = cryptoslate_analyzer.get_sentiment()
        
        # Get Bitcoin price data
        try:
            price_data = price_service.get_bitcoin_price()
        except Exception as e:
            print(f"Warning: Failed to fetch price data: {e}")
            price_data = None
        
        # Calculate weighted scores
        weighted_fear_greed = fear_greed_score.value * config.sentiment.fear_greed_weight
        weighted_reddit = reddit_score.value * config.sentiment.reddit_weight
        weighted_rss_1 = rss_1_score.value * config.sentiment.rss_weight
        weighted_rss_2 = rss_2_score.value * config.sentiment.rss_2_weight
        
        # Create combined sentiment result
        combined = CombinedSentiment(
            fear_greed_score=fear_greed_score,
            price_data=price_data,
            weighted_fear_greed=weighted_fear_greed,
            reddit_score=reddit_score.value,
            rss_1_score=rss_1_score.value,
            rss_2_score=rss_2_score.value,
            final_score=weighted_fear_greed + weighted_reddit + weighted_rss_1 + weighted_rss_2,
            timestamp=datetime.now(tz=timezone('Asia/Singapore'))
        )
        
        # Append to Google Sheets
        result = append_to_sheet(config.api_config.spreadsheet_id, "Sheet1!A:K", [combined.to_sheet_row()])
        
        if result:
            print(f"Successfully appended data to sheets")
            print(f"Fear & Greed Score: {combined.fear_greed_score.value:.2f}")
            print(f"Reddit Sentiment Score: {combined.reddit_score.value:.2f}")
            print(f"CoinTelegraph RSS Score: {combined.rss_1_score.value:.2f}")
            print(f"CryptoSlate RSS Score: {combined.rss_2_score.value:.2f}")
            print(f"Final Weighted Score: {combined.final_score:.2f}")
        else:
            print("Failed to append data to sheets")
            
    except SentimentAnalysisError as e:
        print(f"Sentiment analysis error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    collect_and_append_sentiment()