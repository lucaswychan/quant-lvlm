import yfinance as yf
import json
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

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

def get_news_content(news_url: str) -> str:
    response = requests.get(news_url)
    if response.status_code != 200:
        print(f"Failed to get content from {news_url} with status code {response.status_code}")
        return ""

    soup = BeautifulSoup(response.content, 'html.parser')

    content = soup.find("div", class_="caas-body")

    text = content.text
    words_to_remove = ["Story continues", "View comments"]
    for word in words_to_remove:
        text = text.replace(word, "")
    
    return text
    

def process_news(tickers_news: dict[str, pd.DataFrame]):
    for ticker, news_df in tickers_news.items():
        print(f"Processing news for {ticker}")
        for url in news_df["link"]:
            print(url)
            content = get_news_content(url)
            print(content)
            print("="*50)
    

if __name__ == "__main__":
    tickers = ["AAPL", "GOOGL", "AMZN"]
    tickers_news = get_news(tickers)
    process_news(tickers_news)