from news_scrapper import FinanceNewsScrapper
from notion import NotionClient
from llama_vision import LlamaVision
import json
from datetime import datetime
from prompt_template import PROMPT_TEMPLATE

def main():
    notion = NotionClient()
    scrapper = FinanceNewsScrapper()
    vlm = LlamaVision()
    
    with open("tickers.json", "r") as f:
        tickers = json.load(f)["tickers"]
    
    tickers_news = scrapper.scrap(tickers)
    
    today = datetime.today().strftime("%m-%d-%Y")
    sub_page_title = f"{today} - Finance News"
    # subpages = notion.create_page(sub_page_title)
    
    for ticker, news in tickers_news.items():
        for i, (title, news_contents) in enumerate(news.items()):
            news_text, image, news_url = news_contents
            
            prompt = PROMPT_TEMPLATE.format(title=title, news_text=news_text)
            
            vlm_response = vlm(prompt, image)
            
            print(vlm_response)
            
            print("===============\n\n")
    
if __name__ == "__main__":
    main()