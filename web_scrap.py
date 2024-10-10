import requests

_END_POINT = "https://finance.yahoo.com/quote/{}"

def scrap_news(code: str) -> list[str]:
    response = requests.get(_END_POINT.format(code))