# quant-lvlm

Leveraging large vision language models (LVLM) for quantitative analysis. Current function include finance news article analysis and summarization.

## Finance News Analysis
Employing LVLM to summarize and analyze finance news articles. The data are retrieved from Yahoo Finance website. Furthermore, sentiment analysis is performed by LVLM on the news article. The output is summarized and sent to the Notion database.

The `.env` file in the root directory will be required. The format is as follows:

```
NOTION_TOKEN = <your notion API token>
NOTION_PAGE_ID = <your notion page ID of the page you want to add the news>
```

By changing the desired tickers in [`tickers.json`](tickers.json), you can analyze multiple stocks.

## Time Series Analysis
Stay tuned.

## TODO
Please visit [TODO.md](TODO.md) for more information.