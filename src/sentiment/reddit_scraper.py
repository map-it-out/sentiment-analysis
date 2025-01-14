import praw
import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Download necessary NLTK resources
nltk.download('vader_lexicon', quiet=True)

class RedditSentimentScraper:
    def __init__(self, client_id, client_secret, user_agent):
        """
        Initialize Reddit API connection and sentiment analyzer
        
        :param client_id: Reddit API client ID
        :param client_secret: Reddit API client secret
        :param user_agent: Unique user agent string
        """
        # Initialize Reddit instance
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        # Initialize sentiment analyzer
        self.sia = SentimentIntensityAnalyzer()
    
    def scrape_posts(self, query, limit=100, subreddit=None):
        """
        Scrape Reddit posts and perform sentiment analysis
        
        :param query: Search query
        :param limit: Maximum number of posts to retrieve
        :param subreddit: Optional specific subreddit to search
        :return: DataFrame with posts and sentiment analysis
        """
        # Prepare to store results
        posts_data = []
        
        try:
            # Determine search method based on subreddit parameter
            if subreddit:
                # Search within a specific subreddit
                submissions = self.reddit.subreddit(subreddit).search(query, limit=limit)
            else:
                # Search across all Reddit
                submissions = self.reddit.subreddit('all').search(query, limit=limit)
            
            # Process each submission
            for submission in submissions:
                # Perform sentiment analysis on title and selftext
                title_sentiment = self.sia.polarity_scores(submission.title)
                
                # Only analyze self text if it exists
                selftext_sentiment = self.sia.polarity_scores(submission.selftext) if submission.selftext else None
                
                # Compile post data
                post_data = {
                    'title': submission.title,
                    'text': submission.selftext,
                    'url': submission.url,
                    'score': submission.score,
                    'num_comments': submission.num_comments,
                    'title_sentiment_compound': title_sentiment['compound'],
                    'title_sentiment_positive': title_sentiment['pos'],
                    'title_sentiment_negative': title_sentiment['neg'],
                    'title_sentiment_neutral': title_sentiment['neu'],
                }
                
                # Add selftext sentiment if available
                if selftext_sentiment:
                    post_data.update({
                        'text_sentiment_compound': selftext_sentiment['compound'],
                        'text_sentiment_positive': selftext_sentiment['pos'],
                        'text_sentiment_negative': selftext_sentiment['neg'],
                        'text_sentiment_neutral': selftext_sentiment['neu'],
                    })
                
                posts_data.append(post_data)
        
        except Exception as e:
            print(f"An error occurred: {e}")
        
        # Convert to DataFrame
        df = pd.DataFrame(posts_data)
        return df
    
    def categorize_sentiment(self, sentiment_score):
        """
        Categorize sentiment score
        
        :param sentiment_score: Compound sentiment score
        :return: Sentiment category
        """
        if sentiment_score > 0.07:
            return 'Positive'
        elif sentiment_score < -0.05:
            return 'Negative'
        else:
            return 'Neutral'
    
    def analyze_overall_sentiment(self, df):
        """
        Analyze overall sentiment of scraped posts
        
        :param df: DataFrame with sentiment scores
        :return: Dictionary with sentiment summary
        """
        # Use title sentiment for analysis
        sentiment_counts = df['title_sentiment_compound'].apply(self.categorize_sentiment).value_counts()
        
        return {
            'total_posts': len(df),
            'sentiment_distribution': sentiment_counts.to_dict(),
            'average_sentiment': df['title_sentiment_compound'].mean()
        }

def main():
    # Replace with your actual Reddit API credentials
    CLIENT_ID = 'bM1xR9xtXugnVqOCd92BPw'
    CLIENT_SECRET = 'tjPX5Ubl5rYzvEffR8dniKiYUwYsCA'
    USER_AGENT = 'jftsnb_'
    
    # Create scraper instance
    scraper = RedditSentimentScraper(CLIENT_ID, CLIENT_SECRET, USER_AGENT)
    
    # Example usage
    query = 'openai'
    
    # Scrape posts
    posts_df = scraper.scrape_posts(query, limit=50)
    
    # Analyze sentiment
    sentiment_summary = scraper.analyze_overall_sentiment(posts_df)
    
    # Print results
    print("Sentiment Analysis Results:")
    print(sentiment_summary)
    
    # Optionally save to CSV
    posts_df.to_csv('reddit_sentiment_results.csv', index=False)

if __name__ == '__main__':
    main()