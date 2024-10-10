import yfinance as yf
import json

from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from pyrate_limiter import Duration, RequestRate, Limiter

class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass

session = CachedLimiterSession(
    limiter=Limiter(RequestRate(10, Duration.SECOND*5)),  # max 2 requests per 5 seconds
    bucket_class=MemoryQueueBucket,
    backend=SQLiteCache("yfinance.cache"),
)

def get_news(tickers: list[str]) -> dict:
    tickers_obj = yf.Tickers(tickers, session=session)
    return tickers_obj.news



if __name__ == "__main__":
    voo = yf.Ticker("NVDA")
    print(voo.news)
    news_dict = {"news": voo.news}
    
    with open("news.json", "w") as f:
        json.dump(news_dict, f, indent=4)