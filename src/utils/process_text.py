import re
import emoji
import string
from opencc import OpenCC

def process_text(text):
    """
    Cleans social media text by performing the following:
    - Remove HTML tags
    - Remove URLs
    - Remove punctuation (but keep hashtags)
    - Convert to lowercase
    - Remove stopwords
    - Remove extra whitespace
    - Remove emojis
    - Convert Traditional Chinese to Simplified Chinese

    Args:
        text (str): The input text to clean.

    Returns:
        str: The cleaned text.
    """
    # Initialize OpenCC for Traditional to Simplified Chinese conversion
    cc = OpenCC('t2s')

    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove punctuation but keep hashtags
    text = re.sub(rf"[{re.escape(string.punctuation.replace('#', ''))}]", '', text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove emojis
    text = emoji.replace_emoji(text, replace='')  # Replace emojis with an empty string
    
    # Convert Traditional Chinese to Simplified Chinese
    text = cc.convert(text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text