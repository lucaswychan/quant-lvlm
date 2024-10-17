VLM_ROLE = "You are a financial analyst. You are extremely good at analyzing and summarizing finance news articles."

PROMPT_TEMPLATE = """
    You will be given a finance news article and tile, and an image related to the news article. Your tasks are as follows:
    
    1. Read the news article and title.
    2. Look at the image.
    3. Write a summary of the news article in plain text.
    4. Give the sentiment of the news article. It can be positive, negative, or neutral.
    6. End your summary with a new line.
    
    The Given news title: {title}
    
    The given news article content:
    {news_text}

    Your output should be in the following format:

    <your summary>
    - Sentiment: <positive/negative/neutral>
    
    NOTE: Please make sure your summary is concise and clear. You can write a maximum of 1500 tokens. Only output a plain text summary.
    """
