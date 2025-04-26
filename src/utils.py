import re
import json
from datetime import datetime
import calendar

import nvidia_smi
import torch
import pandas as pd

from notion import NotionClient


def get_available_gpu(use_cpu=True) -> str:
    """
    Get the GPU index which have more than 90% free memory
    """
    # Initialize NVIDIA-SMI
    nvidia_smi.nvmlInit()

    # Get the number of available GPUs
    deviceCount = nvidia_smi.nvmlDeviceGetCount()

    for i in range(deviceCount):
        handle = nvidia_smi.nvmlDeviceGetHandleByIndex(i)
        info = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)

        # Check if the GPU has enough free memory (e.g., 90% free)
        if info.free / info.total > 0.9:
            # Try to allocate a small tensor on this GPU
            try:
                with torch.cuda.device(f"cuda:{i}"):
                    torch.cuda.current_stream().synchronize()
                    torch.cuda.empty_cache()
                    torch.cuda.memory.empty_cache()
                    test_tensor = torch.zeros((1,), device=f"cuda:{i}")
                    del test_tensor
                    return f"cuda:{i}"
            except RuntimeError:
                # If allocation fails, move to the next GPU
                continue

    # If no available GPU is found
    if not use_cpu:
        raise RuntimeError("No available GPU found")

    return "cpu"


def process_news_df(news: pd.DataFrame, day_ago_time: int, today_time: int) -> pd.DataFrame:
    """
    After updating yfinance to 0.2.54, the news' dataframe is changed completely. 
    Now all the meta data of the news are stored in a column "content", with each row a dictionary storing the meta data of a news.
    """
    if news.empty:
        return news
    
    news_content_jsons = list(news["content"])
    with open('news_content.json', 'w') as fp:
        json.dump(list(news_content_jsons)[0], fp, indent=4)
    
    news_content_df = pd.DataFrame(news_content_jsons)
    
    target_columns = ["title", "summary", "pubDate"]
    
    # convert the date to timestamp
    news_content_df = news_content_df[target_columns]

    news_content_df["pubDate"] = news_content_df["pubDate"].apply(
        lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ")
    ).apply(lambda x: calendar.timegm(x.timetuple()))
    
    news_url_list = []
    image_url_list = []
    
    for news_json in news_content_jsons:
        # assign the news_url and image_url
        
        news_url = None
        if news_json.get("canonicalUrl", None) is not None:
            news_url = news_json["canonicalUrl"].get("url")
        
        news_url_list.append(news_url)
        
        image_url = None
        if news_json.get("thumbnail", None) is not None:
            image_url = news_json["thumbnail"].get("originalUrl")
        
        image_url_list.append(image_url)
    
    news_content_df["news_url"] = news_url_list
    news_content_df["image_url"] = image_url_list
    
    # filter the news that published within a time range
    news_content_df = news_content_df[
        (news_content_df["pubDate"] >= day_ago_time)
        & (news_content_df["pubDate"] <= today_time)
    ]
    
    news_content_df.to_csv("processed_news_content.csv", index=False)
    return news_content_df


def notion_add_news_part(
    notion_client: NotionClient,
    page_id: str,
    news_title: str,
    news_summary: str,
    news_url: str,
    ticker: str,
    current_time: str,
):
    """
    Add the news part to the page. There is a certain format for the news part designed by me. You can change to your own format if you want.
    """
    STOCK_DATA_URL = "https://finance.yahoo.com/quote/{}"

    space_obj = {"content_type": "paragraph", "content_text": " "}

    elements_to_be_added = [
        space_obj,
        # Title
        {"content_type": "heading_2", "content_text": news_title, "color": "blue"},
        # Time added
        {
            "content_type": "paragraph",
            "content_text": f"Time added : {current_time}",
            "is_italic": True,
            "color": "gray",
        },
        # Ticker information
        {
            "content_type": "paragraph",
            "content_text": f"Ticker: {ticker}",
            "is_bold": True,
            "is_italic": True,
            "link": STOCK_DATA_URL.format(ticker),
        },
        space_obj,
        # News summary
        {"content_type": "paragraph", "content_text": news_summary},
        space_obj,
        # News URL
        {
            "content_type": "paragraph",
            "content_text": "URL:",
            "is_bold": True,
        },  # Link to the news
        {
            "content_type": "paragraph",
            "content_text": news_url,
            "link": news_url,
            "is_bold": True,
        },
        space_obj,
    ]

    notion_client.add_multiple_elements(page_id, elements_to_be_added)
    notion_client.add_divider(page_id)


if __name__ == "__main__":
    # Usage
    notion = NotionClient()

    sub_page = notion.create_page("Test Page")
    sub_page_id = sub_page["id"]

    notion_add_news_part(
        notion,
        sub_page_id,
        "Title 2: Some news title",
        "Got some summary and conclusion second one. Longer Text : " * 10,
        "https://google.com",
        "TSLA",
    )
