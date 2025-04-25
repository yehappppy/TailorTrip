# from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
# from src.utils.llm import base_llm
# from src.utils.util import structure_output
from typing import List, Dict, Any
import subprocess
import json
import os
import sys
from datetime import datetime

# SEARCH_INFORMATION_PROMPT = """
# 你要假装成为一个搜索引擎。根据用户给定的关键词，你需要：
# 1. 根据关键词编撰出一篇推文
# 2. 确保信息与用户的关键词相关
# 3. 推文中应当包含具体的细节，每次回答的结果相互独立

# 请直接进行输出：
# """

# SAMPLE_INPUT = """
# 日本京都樱花季
# """

# SAMPLE_OUTPUT = """
# 🌸 京都樱花季攻略来啦！2024年预测花期：3月25日-4月5日，比往年稍早！最佳赏樱地：
# 1️⃣ 哲学之道：2公里樱花隧道，夜樱点灯超梦幻
# 2️⃣ 岚山竹林：樱花与竹林的绝妙组合
# 3️⃣ 清水寺：千年古刹+粉色樱花=绝美明信片风景

# 🏨 住宿建议：祗园附近传统町屋，人均¥800/晚，可体验茶道和和服

# 🚆 交通贴士：推荐购买"京都巴士一日券"（¥700），无限次乘坐！

# ⚠️ 注意：热门景点需提前1个月预约，特别是怀石料理餐厅！#京都旅行 #樱花季
# """



# v2: modify search function by using mediacrawler
# def search(keyword: str) -> List[Dict[str, Any]]:
#     llm = base_llm()
#     messages = [
#         SystemMessage(content=SEARCH_INFORMATION_PROMPT),
#         HumanMessage(content=SAMPLE_INPUT),
#         AIMessage(content=SAMPLE_OUTPUT),
#         HumanMessage(content=keyword)
#     ]
#     result = llm.invoke(messages).content
#     return [result]

def tool(func):
    """
    A placeholder decorator for marking functions as tools.
    This can later be extended to include specific functionality.
    """
    def wrapper(*args, **kwargs):
        print(f"Executing tool: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

# 定义 search 工具函数
@tool
def search(keyword: str) -> list[str]:
    """
    A tool function to execute a search using the specified keyword and process the JSON results.
    
    Args:
        keyword (str): The search keyword.
    
    Returns:
        list[str]: A list of strings, each containing information about one post (title, content, comments, OCR).
    """
    try:
        # 获取TailorTrip目录的路径
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.append(root_dir)
        # 获取MediaCrawler目录的路径
        media_crawler_dir = os.path.join(root_dir, "src", "library", "MediaCrawler")
        # 获取main.py的完整路径
        main_script_path = os.path.join(root_dir, "src", "library", "MediaCrawler", "main.py")
        # 调用命令行工具并传入参数
        subprocess.run(
            [
                "python", main_script_path,  # 使用完整path
                "--platform", "xhs", 
                "--lt", "qrcode", 
                "--type", "search", 
                "--keywords", keyword
            ],
            # capture_output=True,
            text=True,
            check=True
        )
        
        # 获取当前日期并格式化
        current_date = datetime.now().strftime("%Y-%m-%d") # YYYY-mm-dd
        
        # 动态生成路径
        # content_json_path = rf"./data/xhs/json/search_contents_{current_date}.json"
        content_json_path = os.path.join(media_crawler_dir, "data", "xhs", "json", f"search_contents_{current_date}.json")
        # comments_json_path = rf"./data/xhs/json/search_comments_{current_date}.json"
        comments_json_path = os.path.join(media_crawler_dir, "data", "xhs", "json", f"search_comments_{current_date}.json")
        # images_folder_path = rf"./data/xhs/images"
        images_folder_path = os.path.join(media_crawler_dir, "data", "xhs", "images")
        output_txt_path = os.path.join(media_crawler_dir, "sample_output", f"output_{keyword}.txt")
        
        # 加载JSON数据
        with open(content_json_path, 'r', encoding='utf-8') as f:
            contents = json.load(f)
        
        with open(comments_json_path, 'r', encoding='utf-8') as f:
            comments = json.load(f)
        
        # 创建一个字典，将评论按note_id组织
        comments_by_note_id = {}
        for comment in comments:
            note_id = comment["note_id"]
            if note_id not in comments_by_note_id:
                comments_by_note_id[note_id] = []
            comments_by_note_id[note_id].append(comment["content"])
        
        # 过滤内容，只保留source_keyword与keyword匹配的条目
        filtered_contents = []
        seen_titles = set()
        for content in contents:
            if content.get("source_keyword") == keyword and content["title"] not in seen_titles:
                filtered_contents.append(content)
                seen_titles.add(content["title"])
        
        # 存储所有帖子信息的列表，每个元素包含一个帖子的完整信息
        post_list = []
        # 生成最终文本内容
        output_lines = []
        
        for content in filtered_contents:
            note_id = content["note_id"]
            title = content["title"]
            desc = content["desc"]
            
            # 创建单个帖子的内容
            post_lines = []
            
            # 写标题
            post_lines.append(f"标题：{title}")
            
            # 写内容
            post_lines.append("内容：")
            post_lines.append(f"{desc}")
            
            # 写评论
            post_lines.append("评论：")
            if note_id in comments_by_note_id:
                for comment in comments_by_note_id[note_id]:
                    post_lines.append(comment)
            else:
                post_lines.append("暂无评论")
            
            # 写OCR识别结果
            post_lines.append("OCR识别结果：")
            note_folder_path = os.path.join(images_folder_path, note_id)
            if os.path.exists(note_folder_path):
                for txt_file in os.listdir(note_folder_path):
                    if txt_file.endswith(".txt"):
                        txt_file_path = os.path.join(note_folder_path, txt_file)
                        with open(txt_file_path, 'r', encoding='utf-8') as tf:
                            ocr_content = tf.read()
                            post_lines.append(ocr_content)
            else:
                post_lines.append("暂无OCR识别结果")
            
            # 将这个帖子的信息添加到列表中
            post_content = "\n".join(post_lines)
            post_list.append(post_content)
            
            # 添加到输出文件的内容中，包括分隔符
            output_lines.extend(post_lines)
            output_lines.append("\n" + "="*50 + "\n")
        
        # 将所有内容写入文件
        with open(output_txt_path, 'w', encoding='utf-8') as output_file:
            output_file.write("\n".join(output_lines))
        
        # 返回关键词对应爬取到的帖子的列表，每个元素对应一个帖子（标题 内容 评论 ocr合起来）的字符串
        return post_list
    
    except subprocess.CalledProcessError as e:
        # 捕获错误并返回错误信息
        return [f"Error: {e.stderr.strip()}"]
    except FileNotFoundError as e:
        return [f"Error: File not found - {e}"]
    except json.JSONDecodeError as e:
        return [f"Error: Failed to decode JSON - {e}"]


###### 示例调用：######
# # 获取TailorTrip的绝对路径并将TailorTrip添加到路径
# import os
# import sys
# import time
# current_dir = os.path.dirname(os.path.abspath(__file__))  # tools目录
# src_parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))  # TailorTrip目录
# sys.path.append(src_parent_dir)
# from src.library.MediaCrawler.config.base_config import KEYWORDS
# time0=time.time()
# KEYWORDS = "曾母暗沙旅游" # str; 可修改为任意关键词
# result = search(KEYWORDS)  # search(keyword: str) -> List[str]
# time1=time.time()
# print(f"finish: cost {time1-time0: .2f} seconds")
# print(result) # List[str]