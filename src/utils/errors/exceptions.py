"""Custom exceptions for the sentiment analysis system"""

class SentimentAnalysisError(Exception):
    """Base exception for all sentiment analysis errors"""
    pass

class APIError(SentimentAnalysisError):
    """Exception raised for errors in API calls"""
    pass

class ConfigurationError(SentimentAnalysisError):
    """Exception raised for configuration-related errors"""
    pass

class DataFetchError(APIError):
    """Exception raised when failing to fetch data from external sources"""
    pass

class DataProcessingError(SentimentAnalysisError):
    """Exception raised when failing to process or analyze data"""
    pass
