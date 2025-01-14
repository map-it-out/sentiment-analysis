import praw
import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import os
from dotenv import load_dotenv

class RedditSentimentAnalyzer:
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
    
    def analyze_sentiment(self, df: pd.DataFrame) -> dict:
        """
        Analyze overall sentiment of posts
        
        Args:
            df: DataFrame containing post data
            
        Returns:
            Dictionary with sentiment summary
        """
        if df.empty:
            return {'error': 'No data available for analysis'}
        
        def categorize_sentiment(score):
            if score > 0.05:
                return 'Positive'
            elif score < -0.05:
                return 'Negative'
            return 'Neutral'
        
        sentiment_counts = df['title_sentiment_compound'].apply(categorize_sentiment).value_counts()
        
        return {
            'total_posts': len(df),
            'sentiment_distribution': sentiment_counts.to_dict(),
            'average_sentiment': df['title_sentiment_compound'].mean()
        }
    
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
            sentiment_summary = analyzer.analyze_sentiment(posts_df)
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