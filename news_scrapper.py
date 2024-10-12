import json
from datetime import datetime
from io import BytesIO
from typing import Optional

import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup
from PIL import Image
from pyrate_limiter import Duration, Limiter, RequestRate
from requests import Session
from requests.adapters import HTTPAdapter
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from urllib3.util import Retry

_HEADER = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0.1 Safari/605.1.15"
}
_ONE_DAY = 86400


def initialize():
    global session

    class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
        pass

    session = CachedLimiterSession(
        limiter=Limiter(
            RequestRate(10, Duration.SECOND * 5)
        ),  # max 10 requests per 5 seconds
        bucket_class=MemoryQueueBucket,
        backend=SQLiteCache("yfinance.cache"),
    )

    retry = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
    )

    adapter = HTTPAdapter(max_retries=retry)

    session = Session()
    session.mount("https://", adapter)


initialize()


def get_news_obj(tickers: list[str]) -> dict[str, pd.DataFrame]:
    today_time = datetime.now()
    # convert to unix timestamp
    today_time = int(today_time.timestamp())
    one_day_ago_time = today_time - _ONE_DAY

    # filter the news that published within 24 hours
    def filter_time(news: pd.DataFrame) -> pd.DataFrame:
        if news.empty:
            return news

        news = news[
            (news["providerPublishTime"] >= one_day_ago_time)
            & (news["providerPublishTime"] <= today_time)
        ]
        return news

    tickers_obj = yf.Tickers(tickers, session=session)
    tickers_news = {
        ticker: filter_time(pd.DataFrame(news))
        for ticker, news in tickers_obj.news().items()
    }

    return tickers_news


def get_each_news_content(news_url: str) -> tuple[str, Optional[Image.Image]]:
    response = session.get(news_url, headers=_HEADER)

    if response.status_code != 200:
        return (
            f"Failed to get content from {news_url} with status code {response.status_code}. Please check the URL.",
            None,
        )

    soup = BeautifulSoup(response.content, "html.parser")

    text = ""
    image = None

    # get the text
    if text_element := soup.find("div", class_="caas-body"):
        text = text_element.text
        words_to_remove = ["Story continues", "View comments"]
        for word in words_to_remove:
            text = text.replace(word, "")

    # get the image
    if image_element := soup.find("img", class_="caas-img has-preview"):
        image_url = image_element["src"]
        response = session.get(image_url)
        image = Image.open(BytesIO(response.content))

    return text, image


def scrap_news(tickers: list[str]):
    tickers_news = get_news_obj(tickers)
    ticker_news_map = {}

    for ticker, news_df in tickers_news.items():
        print(f"Processing news for {ticker}")

        ticker_news_map[ticker] = {}

        for i in range(len(news_df)):
            title, url = news_df.iloc[i][["title", "link"]]
            contents = get_each_news_content(url)

            ticker_news_map[ticker][title] = contents

    return ticker_news_map


if __name__ == "__main__":
    with open("tickers.json", "r") as f:
        tickers = json.load(f)

    news = scrap_news(tickers["tickers"])
