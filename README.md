# quant-lvlm

Leveraging large vision language models (LVLM) for quantitative analysis. Currently supports finance news article analysis and summarization.

- [Finance News Analysis](#finance-news-analysis)
- [Time Series Analysis](#time-series-analysis)

## Get Started

Clone this repository

```
git clone https://github.com/lucaswychan/quant-lvlm
cd quant-lvlm
```

Then install all Python Packages by running:

```
pip install -r requirements.txt
```

Finally create your own `.env` file in the root directory.

```
touch .env
```

## Finance News Analysis
Employing LVLM to summarize and analyze finance news articles. The data are retrieved from [Yahoo Finance website](https://finance.yahoo.com/). Furthermore, sentiment analysis is performed by LVLM on the news article. The output is summarized and sent to the[ Notion database](https://www.notion.com).

### Setup

The `.env` file in the root directory will be required. The format is as follows:

```
NOTION_TOKEN = <your notion API token>
NOTION_PAGE_ID = <your notion page ID of the page you want to add the news>
```

To get the `NOTION_TOKEN`, you have to first create a [notion connection](https://www.notion.so/profile/integrations) for your page. You can navigate to your own notion app and goto `Settings > Connections > Develop or manage integrations > New integration` or visit [**here**](https://www.notion.so/profile/integrations). Once you create a new integration, copy the token  shown as `Internal Integration Secret` and paste it into your `.env` file.

After creating your connection, you have to link it to your notion page, which will be the page the news will be added. You can either create a new page or use an existing one. Once you have your page, click into the page and navigate to `···` located in the upper right corner. You can see `Connections`, and you can select your newly created connection once you click into it.

To get the `NOTION_PAGE_ID`, navigate to `···` located in the upper right corner again and click `Copy link`. You will see an url in the format of:

```
https://www.notion.so/You_Page_Name-xxxxxxxxxxxxxxxxxxxxxxxxxxxx?pvs=4
```

The long `xxxxxxxxxxxxxxxxxxxxxxxxxxxx` is your `NOTION_PAGE_ID` of that page.

By changing the desired tickers in [`tickers.json`](tickers.json), you can analyze multiple stocks.

### Usage

Simple usage:
```
python3 quant_news.py
```
  

For added convenience, you can utilize the [Shortcut](https://support.apple.com/guide/shortcuts/welcome/ios) app on your iPhone to execute the script without needing to enter commands in a terminal. In my case, I created a shortcut that connects to a server and runs the script remotely. This approach leverages the power of iOS Shortcuts to simplify the process of running scripts on the server.

The Shortcuts app, as described in Apple's Shortcuts User Guide, allows you to create custom automations that can perform complex tasks with just a tap. By setting up a shortcut for your server connection and script execution, you can streamline your workflow and run your scripts more efficiently.

<img src="assests/iphone_shortcut.jpg" style="width: 50%; margin: auto; display: block;">


## Time Series Analysis
Stay tuned.

## TODO
Please visit [TODO.md](TODO.md) for more information.