import re

import nvidia_smi
import torch

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
