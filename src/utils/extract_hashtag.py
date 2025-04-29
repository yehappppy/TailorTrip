import re

def extract_hashtags(text):
    """Extract all hashtags with regular expressions"""
    hashtags = re.findall(r'#(\S+)', text)
    return hashtags