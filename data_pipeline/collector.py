import os
import json
from datetime import datetime
from instagrapi import Client
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self):
        self.cl = Client()
        self.instagram_authenticated = False

    def authenticate_instagram(self):
        try:
            self.cl.login(
                os.getenv('INSTAGRAM_USERNAME'),
                os.getenv('INSTAGRAM_PASSWORD')
            )
            self.instagram_authenticated = True
        except Exception as e:
            logger.error(f"Instagram authentication failed: {str(e)}")

    def fetch_instagram_posts(self, hashtag: str, limit: int = 100) -> List[Dict]:
        if not self.instagram_authenticated:
            self.authenticate_instagram()
        
        posts = self.cl.hashtag_medias_recent(hashtag, amount=limit)
        return [self._process_post(p) for p in posts]

    def _process_post(self, post) -> Dict:
        return {
            'id': post.id,
            'caption': post.caption_text,
            'location': post.location.name if post.location else None,
            'timestamp': post.taken_at.isoformat(),
            'likes': post.like_count,
            'comments': post.comment_count,
            'url': post.video_url if post.media_type == 2 else post.thumbnail_url
        }

    def save_raw_data(self, data: List[Dict], prefix: str = "posts"):
        os.makedirs('data/raw', exist_ok=True)
        filename = f"data/raw/{prefix}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(data, f)
        logger.info(f"Saved raw data to {filename}")
