import json
from datetime import datetime

from llama_vision import LlamaVision
from news_scrapper import FinanceNewsScrapper
from notion import NotionClient
from prompt_template import PROMPT_TEMPLATE
from utils import notion_add_news_part


def main():
    notion = NotionClient()
    scrapper = FinanceNewsScrapper()
    vlm = LlamaVision()

    with open("tickers.json", "r") as f:
        tickers = json.load(f)["tickers"]

    tickers_news = scrapper.scrap(tickers)

    today = datetime.today().strftime("%m-%d-%Y")
    sub_page_title = f"{today} - Finance News"
    sub_pages = notion.create_page(sub_page_title)
    sub_pages_id = sub_pages["id"]

    for ticker, news in tickers_news.items():
        for news_title, news_contents in news.items():
            news_text, image, news_url = news_contents

            prompt = PROMPT_TEMPLATE.format(title=news_title, news_text=news_text)

            vlm_response = vlm(prompt, image)

            notion_add_news_part(
                notion, sub_pages_id, news_title, vlm_response, news_url, ticker
            )


if __name__ == "__main__":
    main()
