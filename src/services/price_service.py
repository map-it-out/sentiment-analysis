"""Service for fetching cryptocurrency price data"""
from datetime import datetime
import requests
from src.utils.errors.exceptions import DataFetchError
# TODO: Restructure foldering
from src.models.models import PriceData
from src.config.config import config

class CryptoPriceService:
    """Service for fetching cryptocurrency price data"""
    
    def __init__(self, api_url: str = None):
        self.api_url = api_url or config.api.bitcoin_price_api_url
    
    def get_bitcoin_price(self) -> PriceData:
        """Fetch current Bitcoin price and related metrics"""
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()
            data = response.json()
            
            btc_data = data['data']['1']  # 1 is the ID for Bitcoin
            current_price = float(btc_data['quotes']['USD']['price'])
            
            # Calculate price changes
            change_1h = float(btc_data['quotes']['USD']['percentage_change_1h']) / 100
            change_24h = float(btc_data['quotes']['USD']['percentage_change_24h']) / 100
            
            price_1h = current_price / (1 + change_1h)
            price_24h = current_price / (1 + change_24h)
            
            return PriceData(
                current_price=current_price,
                price_1h=price_1h,
                price_24h=price_24h,
                change_1h=change_1h,
                change_24h=change_24h,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            raise DataFetchError(f"Failed to fetch Bitcoin price data: {str(e)}")

# Global service instance
price_service = CryptoPriceService()
