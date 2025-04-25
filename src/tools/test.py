# crawl.py
import os
import sys
from datetime import datetime

current_date = datetime.now().strftime("%Y-%m-%d")
# 获取TailorTrip目录的路径
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)

# 获取main.py的完整路径
main_script_path = os.path.join(root_dir, "src", "library", "MediaCrawler", "main.py")
media_crawler_dir = os.path.join(root_dir, "src", "library", "MediaCrawler")
content_json_path = os.path.join(media_crawler_dir, "data", "xhs", "json", f"search_contents_{current_date}.json")
# comments_json_path = rf"./data/xhs/json/search_comments_{current_date}.json"
comments_json_path = os.path.join(media_crawler_dir, "data", "xhs", "json", f"search_comments_{current_date}.json")
# images_folder_path = rf"./data/xhs/images"
images_folder_path = os.path.join(media_crawler_dir, "data", "xhs", "images")
print(main_script_path)
print(content_json_path)
print(comments_json_path)
print(images_folder_path)

# 然后使用绝对导入
from src.library.MediaCrawler.config.base_config import KEYWORDS
print("yes")