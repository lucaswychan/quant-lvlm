import yfinance as yf
import json
import requests
import pandas as pd
from datetime import datetime

from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from pyrate_limiter import Duration, RequestRate, Limiter

class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass

session = CachedLimiterSession(
    limiter=Limiter(RequestRate(10, Duration.SECOND*5)),  # max 10 requests per 5 seconds
    bucket_class=MemoryQueueBucket,
    backend=SQLiteCache("yfinance.cache"),
)

def get_news(tickers: list[str]) -> dict[str, pd.DataFrame]:
    today_time = datetime.now()
    # convert to unix timestamp
    today_time = int(today_time.timestamp())
    one_day_ago_time = today_time - 86400
    
    # filter the news that published within 24 hours
    def filter_time(news: pd.DataFrame) -> pd.DataFrame:
        news = news[(news["providerPublishTime"] >= one_day_ago_time) & (news["providerPublishTime"] <= today_time)]
        return news

    tickers_obj = yf.Tickers(tickers, session=session)
    tickers_news = {ticker: filter_time(pd.DataFrame(news)) for ticker, news in tickers_obj.news().items()}
    
    return tickers_news

def get_news_contents(news_url):
    response = requests.get(news_url)
    if response.status_code == 200:
        return response.text
    else:
        return None
    

def process_news(tickers_news: dict[str, pd.DataFrame]):
    for ticker, news_df in tickers_news.items():
        pass
    

if __name__ == "__main__":
    tickers = ["AAPL", "GOOGL", "AMZN"]
    get_news(tickers)