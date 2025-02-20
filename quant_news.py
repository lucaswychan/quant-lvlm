import json
from datetime import datetime

from src.models.llama_vision import LlamaVision
from src.news_scrapper import FinanceNewsScrapper
from src.notion import NotionClient
from src.config import PROMPT_TEMPLATE, VLM_ROLE
from src.utils import notion_add_news_part


def main():
    notion = NotionClient()
    scrapper = FinanceNewsScrapper()
    vlm = LlamaVision()

    with open("tickers.json", "r") as f:
        tickers = json.load(f)["tickers"]

    tickers_news = scrapper.scrap(tickers)

    today = datetime.today().strftime("%Y-%m-%d")
    sub_page_title = f"{today} - Finance News"
    sub_pages = notion.create_page(sub_page_title)
    sub_pages_id = sub_pages["id"]

    for ticker, news in tickers_news.items():
        for news_title, news_contents in news.items():
            news_text, news_image, news_url = news_contents

            prompt = PROMPT_TEMPLATE.format(title=news_title, news_text=news_text)

            vlm_response = vlm(VLM_ROLE, prompt, news_image)

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            notion_add_news_part(
                notion,
                sub_pages_id,
                news_title,
                vlm_response,
                news_url,
                ticker,
                current_time,
            )


if __name__ == "__main__":
    main()
