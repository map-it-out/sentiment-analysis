import praw
import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import os
from dotenv import load_dotenv
from src.sentiment.base_analyzer import BaseSentimentAnalyzer, SentimentResult
from datetime import datetime

class RedditSentimentAnalyzer(BaseSentimentAnalyzer):
    """Reddit sentiment analyzer for cryptocurrency discussions"""
    
    def __init__(self):
        """Initialize with environment variables for API credentials"""
        load_dotenv()
        
        self._initialize_nltk()
        self._initialize_reddit()
        self.sia = SentimentIntensityAnalyzer()
    
    def _initialize_nltk(self):
        """Download required NLTK data"""
        try:
            nltk.data.find('sentiment/vader_lexicon.zip')
        except LookupError:
            nltk.download('vader_lexicon', quiet=True)
    
    def _initialize_reddit(self):
        """Initialize Reddit API connection"""
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT'),
            read_only=True,
            check_for_async=False  # Explicitly disable async check
        )
    
    def scrape_posts(self, 
                    query: str = 'bitcoin', 
                    limit: int = 100, 
                    subreddit: str = 'CryptoCurrency',
                    sort: str = 'new') -> pd.DataFrame:
        """
        Scrape and analyze Reddit posts
        
        Args:
            query: Search query string
            limit: Maximum number of posts to retrieve
            subreddit: Subreddit to fetch posts from
            sort: Sorting method ('new', 'hot', 'top', 'rising')
            
        Returns:
            DataFrame containing post data and sentiment analysis
        """
        posts_data = []
        subreddit_instance = self.reddit.subreddit(subreddit)
        
        # Get posts based on sort method
        if sort == 'new':
            submissions = subreddit_instance.new(limit=limit)
        elif sort == 'hot':
            submissions = subreddit_instance.hot(limit=limit)
        elif sort == 'top':
            submissions = subreddit_instance.top(limit=limit)
        elif sort == 'rising':
            submissions = subreddit_instance.rising(limit=limit)
        else:
            submissions = subreddit_instance.new(limit=limit)
        
        for submission in submissions:
            # Analyze sentiment
            title_sentiment = self.sia.polarity_scores(submission.title)
            selftext_sentiment = self.sia.polarity_scores(submission.selftext) if submission.selftext else None
            
            # Compile post data
            post_data = {
                'title': submission.title,
                'text': submission.selftext,
                'score': submission.score,
                'num_comments': submission.num_comments,
                'title_sentiment_compound': title_sentiment['compound'],
                'title_sentiment_pos': title_sentiment['pos'],
                'title_sentiment_neg': title_sentiment['neg'],
                'title_sentiment_neu': title_sentiment['neu']
            }
            
            if selftext_sentiment:
                post_data.update({
                    'text_sentiment_compound': selftext_sentiment['compound'],
                    'text_sentiment_pos': selftext_sentiment['pos'],
                    'text_sentiment_neg': selftext_sentiment['neg'],
                    'text_sentiment_neu': selftext_sentiment['neu']
                })
            
            posts_data.append(post_data)
        
        return pd.DataFrame(posts_data)
    
    def get_sentiment(self) -> SentimentResult:
        """Get sentiment analysis from Reddit posts"""
        try:
            # Fetch and analyze posts
            df = self.scrape_posts()
            if df.empty:
                return SentimentResult(
                    value=0.0,
                    classification="Neutral",
                    interpretation="No data available for analysis",
                    raw_data={'error': 'No data available'},
                    timestamp=datetime.now().isoformat()
                )
            
            def categorize_sentiment(score):
                if score > 0.05:
                    return 'Positive'
                elif score < -0.05:
                    return 'Negative'
                return 'Neutral'
            
            # Calculate combined sentiment from both title and content
            title_sentiments = df['title_sentiment_compound']
            content_sentiments = df.get('text_sentiment_compound', pd.Series([0] * len(df)))
            
            # Weight title sentiment more heavily (0.6) than content sentiment (0.4)
            combined_sentiments = title_sentiments * 0.6 + content_sentiments * 0.4
            
            # Calculate sentiment distribution using combined sentiment
            sentiment_counts = combined_sentiments.apply(categorize_sentiment).value_counts()
            
            # Use combined sentiment for the overall value
            sentiment_value = combined_sentiments.mean()
            classification = self.classify_sentiment(sentiment_value)
            
            interpretation = f"{classification} - Reddit sentiment is "
            if sentiment_value > 0:
                interpretation += "positive, showing optimistic market signals"
            elif sentiment_value < 0:
                interpretation += "negative, showing pessimistic market signals"
            else:
                interpretation += "neutral, showing balanced market signals"
            
            return SentimentResult(
                value=sentiment_value,
                classification=classification,
                interpretation=interpretation,
                raw_data={
                    'total_posts': len(df),
                    'sentiment_distribution': sentiment_counts.to_dict(),
                    'average_sentiment': sentiment_value,
                    'title_sentiment_mean': title_sentiments.mean(),
                    'content_sentiment_mean': content_sentiments.mean()
                },
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            return SentimentResult(
                value=0.0,
                classification="Error",
                interpretation=f"Failed to analyze Reddit feed: {str(e)}",
                raw_data={"error": str(e)},
                timestamp=datetime.now().isoformat()
            )
    
    def save_results(self, df: pd.DataFrame, filename: str = 'reddit_sentiment_results.csv'):
        """Save analysis results to CSV"""
        df.to_csv(filename, index=False)
        print(f"Results saved to {filename}")

def main():
    """Main function to demonstrate sentiment analysis"""
    analyzer = RedditSentimentAnalyzer()
    
    # Try different sorting methods
    for sort_method in ['new', 'hot', 'top', 'rising']:
        print(f"\nTrying {sort_method} posts...")
        posts_df = analyzer.scrape_posts(sort=sort_method, limit=50)
        
        if not posts_df.empty:
            print(f"Successfully retrieved posts using {sort_method} sorting")
            sentiment_summary = analyzer.get_sentiment()
            print("\nSentiment Analysis Results:")
            print(sentiment_summary)
            
            # Save results
            output_file = f'reddit_sentiment_{sort_method}.csv'
            posts_df.to_csv(output_file, index=False)
            print(f"\nResults saved to {output_file}")
            break
    else:
        print("\nFailed to retrieve posts with any sorting method")

if __name__ == '__main__':
    main()