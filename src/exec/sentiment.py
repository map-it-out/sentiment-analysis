from datetime import datetime
from pytz import timezone
import os
from dotenv import load_dotenv

from src.sentiment.fear_greed_index import CNNFearGreedFetcher, FearGreedAnalyzer
from src.sentiment.reddit_analyzer import RedditSentimentAnalyzer
from src.utils.sheets.sheets_writer import append_to_sheet
from src.const.url import FNG_API_URL
import requests

#TODO: Refactor code
def get_bitcoin_price():
    """Fetch Bitcoin price data from Alternative.me API"""
    try:
        response = requests.get('https://api.alternative.me/v2/ticker/?limit=1')
        response.raise_for_status()
        data = response.json()
        
        btc_data = data['data']['1']  # 1 is the ID for Bitcoin
        current_price = float(btc_data['quotes']['USD']['price'])
        price_1h = current_price * (1 + float(btc_data['quotes']['USD']['percentage_change_1h']) / 100)
        price_24h = current_price * (1 + float(btc_data['quotes']['USD']['percentage_change_24h']) / 100)
        
        return current_price, price_1h, price_24h
    except Exception as e:
        print(f"Error fetching Bitcoin price: {str(e)}")
        return None, None, None

def collect_and_append_sentiment():
    """Collect all sentiment scores and append them to Google Sheets"""
    load_dotenv()
    
    # Initialize analyzers
    fear_greed_fetcher = CNNFearGreedFetcher(FNG_API_URL)
    fear_greed_analyzer = FearGreedAnalyzer(fear_greed_fetcher)
    # reddit_analyzer = RedditSentimentAnalyzer()
    
    try:
        # Get Fear & Greed sentiment
        fear_greed_sentiment = fear_greed_analyzer.get_sentiment()
        fear_greed_score = (fear_greed_sentiment.value + 1) / 2  # Convert from [-1, 1] to [0, 1]
        
        # Get Reddit sentiment
        # reddit_df = reddit_analyzer.scrape_posts(query='bitcoin', limit=100)
        # reddit_analysis = reddit_analyzer.analyze_sentiment(reddit_df)
        reddit_analysis = {'overall_sentiment': 0.5} # hardcoded due to Reddit connection issue in Indonesia
        reddit_score = (reddit_analysis['overall_sentiment'] + 1) / 2  # Convert from [-1, 1] to [0, 1]
        
        # Calculate weighted scores (0.5 each)
        weighted_fear_greed = fear_greed_score * 0.5
        weighted_reddit = reddit_score * 0.5
        
        # Calculate final score
        final_score = weighted_fear_greed + weighted_reddit
        
        # Get current BTC price from Alternative.me API
        current_price, price_1h, price_24h = get_bitcoin_price()
        if current_price is None:
            print("Using placeholder values due to price fetch error")
            current_price = 100000
            price_1h = 101500
            price_24h = 103500
        
        # Calculate price changes
        change_1h = (price_1h - current_price) / current_price
        change_24h = (price_24h - current_price) / current_price
        
        # Prepare row for sheets
        row = [
            datetime.now(tz=timezone('Asia/Singapore')).strftime('%Y-%m-%d %H:%M:%S'),
            fear_greed_score,
            reddit_score,
            weighted_fear_greed,
            weighted_reddit,
            final_score,
            current_price,
            price_1h,
            f"{change_1h:.2%}",
            price_24h,
            f"{change_24h:.2%}"
        ]
        
        # Append to Google Sheets
        spreadsheet_id = os.getenv('SPREADSHEET_ID')
        result = append_to_sheet(spreadsheet_id, "Sheet1!A:K", [row])
        
        if result:
            print(f"Successfully appended data to sheets")
            print(f"Fear & Greed Score: {fear_greed_score:.2f}")
            print(f"Reddit Sentiment Score: {reddit_score:.2f}")
            print(f"Final Weighted Score: {final_score:.2f}")
        else:
            print("Failed to append data to sheets")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    collect_and_append_sentiment()