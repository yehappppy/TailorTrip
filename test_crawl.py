
import os
import time
import sys
from src.tools.crawl import crawl
import src.library.MediaCrawler.config as config

current_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"tools")  # tools目录
src_parent_dir = os.path.dirname(os.path.abspath(__file__))  # TailorTrip目录
# print(src_parent_dir)
sys.path.append(src_parent_dir)
print("config.keywords:",config.KEYWORDS)
time0=time.time()
result = crawl(config.KEYWORDS)  
time1=time.time()
print(f"finish: cost {time1-time0: .2f} seconds")
print(result) # 理想情况是List[str]
print("length of output:",len(result))