from news_scrapper import FinanceNewsScrapper
from notion import NotionClient
from llama_vision import LlamaVision
import json
from datetime import datetime

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
    
    prompt = """
    You are a financial analyst. You will be given a finance news article and tile, and an image related to the news article. Your tasks are as follows::
    
    1. Read the news article and title.
    2. Look at the image.
    3. Write a summary of the news article.
    4. Give the sentiment of the news article. It can be positive, negative, or neutral.
    
    New Title: {title}
    
    News Article:
    {news_text}

    Output:
        Summary:
        Sentiment:
    """
    
    for ticker, news in tickers_news.items():
        for i, (title, news_content) in enumerate(news.items()):
            news_text, image = news_content
            
            prompt.format(title=title, news_text=news_text)
            
            vlm_response = vlm(prompt, image)
            
            print(vlm_response)
            
            print("===============\n\n")
    
if __name__ == "__main__":
    main()