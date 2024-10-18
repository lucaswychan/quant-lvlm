VLM_ROLE = "You are a financial analyst with expertise in analyzing and summarizing finance news articles."

PROMPT_TEMPLATE = """
    You will receive a finance news article, title, and an associated image. Your tasks are:

    1. Read the news article and title.
    2. Examine the image.
    3. Write a concise, clear summary of the article in plain text.
    4. Determine the sentiment of the article: positive, negative, or neutral.
    5. End your summary with a newline.
    
    NOTE: Ensure your summary is clear and concise, with a maximum of 1500 tokens. Output only the plain text summary.

    Given news title: {title}

    News article content: {news_text}

    Output format:

    <your summary>
    
    Sentiment: <Positive/Negative/Neutral>
    """
