from datetime import datetime
from pytz import timezone

from src.config import config
from src.models import CombinedSentiment
from src.sentiment.fear_greed_index import CNNFearGreedFetcher, FearGreedAnalyzer
from src.sentiment.reddit_analyzer import RedditSentimentAnalyzer
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
        
        # Get Fear & Greed sentiment
        fear_greed_sentiment = fear_greed_analyzer.get_sentiment()
        
        # Get Reddit sentiment
        reddit_df = reddit_analyzer.scrape_posts(
            query='bitcoin',
            limit=config.sentiment.reddit_post_limit,
            subreddit=config.sentiment.reddit_default_subreddit,
            sort=config.sentiment.reddit_default_sort
        )
        reddit_analysis = reddit_analyzer.analyze_sentiment(reddit_df)
        
        # Get Bitcoin price data
        try:
            price_data = price_service.get_bitcoin_price()
        except Exception as e:
            print(f"Warning: Failed to fetch price data: {e}")
            price_data = None
        
        # Calculate weighted scores
        weighted_fear_greed = fear_greed_sentiment.normalized_score * config.sentiment.fear_greed_weight
        weighted_reddit = reddit_analysis.normalized_score * config.sentiment.reddit_weight
        
        # Create combined sentiment result
        combined = CombinedSentiment(
            fear_greed_score=fear_greed_sentiment,
            reddit_score=reddit_analysis,
            price_data=price_data,
            weighted_fear_greed=weighted_fear_greed,
            weighted_reddit=weighted_reddit,
            final_score=weighted_fear_greed + weighted_reddit,
            timestamp=datetime.now(tz=timezone('Asia/Singapore'))
        )
        
        # Append to Google Sheets
        result = append_to_sheet(config.api_config.spreadsheet_id, "Sheet1!A:K", [combined.to_sheet_row()])
        
        if result:
            print(f"Successfully appended data to sheets")
            print(f"Fear & Greed Score: {combined.fear_greed_score.normalized_score:.2f}")
            print(f"Reddit Sentiment Score: {combined.reddit_score.normalized_score:.2f}")
            print(f"Final Weighted Score: {combined.final_score:.2f}")
        else:
            print("Failed to append data to sheets")
            
    except SentimentAnalysisError as e:
        print(f"Sentiment analysis error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    collect_and_append_sentiment()