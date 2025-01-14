from dotenv import load_dotenv

load_dotenv()

FNG_API_URL: str = "https://api.alternative.me/fng/"
REDDIT_RSS_FEED_URL: str = "https://www.reddit.com/r/wallstreetbets/.rss"
RSS_FEED_URL: str = "https://rss.app/feeds/v1.1"
RSS_FEEDS: dict = {
    "CoinTelegraph": f"{RSS_FEED_URL}/{os.getenv('COIN_TELEGRAPH_RSS_ID')}.json",
    "CryptoSlate": f"{RSS_FEED_URL}/{os.getenv('CRYPTO_SLATE_RSS_ID')}.json"
}