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


class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass


class FinanceNewsScrapper:
    def __init__(self, time_range=86400):
        # constant variables
        self.HEADER = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0.1 Safari/605.1.15"
        }
        self.time_range = time_range

        # session variables
        self.yf_session = CachedLimiterSession(
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

        self.requests_session = Session()
        self.requests_session.mount("https://", adapter)

    def scrap(self, tickers: list[str], verbose=True) -> dict[str, dict]:
        """
        Scrap the news for each ticker in the list. The news will be stored in a dictionary where the key is the ticker and the value is another dictionary where the key is the title of the news and the value is the content of the news.
        """
        tickers_news = self._get_news_obj(tickers)
        ticker_news_map = {}

        for ticker, news_df in tickers_news.items():
            if verbose:
                print(f"Processing news for {ticker}")

            ticker_news_map[ticker] = {}

            for i in range(len(news_df)):
                title, url = news_df.iloc[i][["title", "link"]]
                contents = self._get_each_news_content(url)

                ticker_news_map[ticker][title] = contents

        return ticker_news_map

    def _get_news_obj(self, tickers: list[str]) -> dict[str, pd.DataFrame]:
        """
        Get the news object from yfinance for each ticker. Only news published within <time_range> hours are considered.
        """
        today_time = datetime.now()
        # convert to unix timestamp
        today_time = int(today_time.timestamp())
        one_day_ago_time = today_time - self.time_range

        # filter the news that published within 24 hours
        def filter_time(news: pd.DataFrame) -> pd.DataFrame:
            if news.empty:
                return news

            news = news[
                (news["providerPublishTime"] >= one_day_ago_time)
                & (news["providerPublishTime"] <= today_time)
            ]
            return news

        tickers_obj = yf.Tickers(tickers, session=self.yf_session)
        tickers_news = {
            ticker: filter_time(pd.DataFrame(news))
            for ticker, news in tickers_obj.news().items()
        }

        return tickers_news

    def _get_each_news_content(
        self, news_url: str
    ) -> tuple[str, Optional[Image.Image]]:
        """
        Get the text and image from the news_url. Only one news is processed in this function.
        """
        response = self.requests_session.get(news_url, headers=self.HEADER)

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
            response = self.requests_session.get(image_url)
            image = Image.open(BytesIO(response.content))

        return text, image


if __name__ == "__main__":
    with open("tickers.json", "r") as f:
        tickers = json.load(f)

    scrapper = FinanceNewsScrapper()

    news = scrapper.scrap(tickers["tickers"])
