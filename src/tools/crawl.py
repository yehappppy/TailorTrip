from langchain_core.tools import tool # 记得取消注释!
from langchain_core.messages import HumanMessage,AIMessage,SystemMessage
from typing import List, Dict, Any
from datetime import datetime
import subprocess
import json
import os
import sys
import time
import platform

from src.utils.llm import base_llm

# Check if we're on Windows
IS_WINDOWS = platform.system() == 'Windows'

def crawl(keyword: str) -> list[str]: 
    """
    A tool function to execute a search using the specified keyword and process the JSON results.
    
    Args:
        keyword (str): The search keyword.
    
    Returns:
        list[str]: A list of formatted strings containing the extracted information of every post.
    """
    try:
        # 获取TailorTrip目录的路径
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # print("root_dir:",root_dir)
        sys.path.append(root_dir)
        # 获取MediaCrawler目录的路径
        media_crawler_dir = os.path.join(root_dir, "src", "library", "MediaCrawler")
        # 获取main.py的完整路径
        main_script_path = os.path.join(root_dir, "src", "library", "MediaCrawler", "main.py")
        # 调用命令行工具并传入参数
        
        subprocess.run(
            [
                "python", main_script_path, 
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
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # 动态生成路径
        # content_json_path = rf"./data/xhs/json/search_contents_{current_date}.json"
        # comments_json_path = rf"./data/xhs/json/search_comments_{current_date}.json"
        # images_folder_path = rf"./data/xhs/images"
        # output_txt_path = rf"./output_test.txt"

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
        
        # 生成最终文本内容
        output_lines = []
        for idx, content in enumerate(filtered_contents):
            note_id = content["note_id"]
            title = content["title"]
            desc = content["desc"]
            
            # 分割帖子
            output_lines.append(f"<blog {idx}>")
            # 写标题
            output_lines.append(f"<title>{title}</title>")
            
            # 写内容
            output_lines.append("<content>")
            output_lines.append(f"{desc}")
            output_lines.append("</content>")
            
            # 写评论
            output_lines.append("<comment>")
            if note_id in comments_by_note_id:
                for comment in comments_by_note_id[note_id]:
                    output_lines.append(comment)
            output_lines.append("</comment>")
            
            # 写OCR识别结果
            output_lines.append("<ocr>")
            note_folder_path = os.path.join(images_folder_path, note_id)
            if os.path.exists(note_folder_path):
                for txt_file in os.listdir(note_folder_path):
                    if txt_file.endswith(".txt"):
                        txt_file_path = os.path.join(note_folder_path, txt_file)
                        with open(txt_file_path, 'r', encoding='utf-8') as tf:
                            ocr_content = tf.read()
                            output_lines.append(ocr_content)
            output_lines.append("</ocr>")
            
            # 添加分隔符
            output_lines.append(f"</blog {idx}>")
            output_lines.append("\n" + "="*70 + "\n")
        
        # 将所有内容写入文件并返回字符串
        with open(output_txt_path, 'w', encoding='utf-8') as output_file:
            str_out = "\n".join(output_lines)
            output_file.write(str_out)
        
        # with open(output_txt_path, 'r', encoding='utf-8') as file:
        #     text = file.read()

        # 按分隔符拆分
        posts = str_out.split("="*50)[:-1] # 删除列表最后一个元素（没有用，一个换行符）
        # return "\n".join(output_lines)
        return posts # a list of strings
    
    except subprocess.CalledProcessError as e:
        # 捕获错误并返回错误信息
        if hasattr(e, 'stderr') and e.stderr:
            return f"Error: {e.stderr.strip()}"
        else:
            return f"Error: Command failed with exit code {e.returncode}"
    except FileNotFoundError as e:
        return f"Error: File not found - {e}"
    except json.JSONDecodeError as e:
        return f"Error: Failed to decode JSON - {e}"
    except OSError as e:
        if IS_WINDOWS and 'shm.dll' in str(e):
            # 使用伪搜索结果代替
            print("PyTorch DLL error detected, using pseudo search results instead.")
            return pesudo_crawl(keyword)
        else:
            return f"Error: OS Error - {e}"
    


###### search函数示例调用：######
# # 获取TailorTrip的绝对路径并将TailorTrip添加到路径
# current_dir = os.path.dirname(os.path.abspath(__file__))  # tools目录
# src_parent_dir = os.path.dirname((os.path.dirname(current_dir)))  # TailorTrip目录
# # print(src_parent_dir)
# sys.path.append(src_parent_dir)
# import src.library.MediaCrawler.config as config
# print("config.keywords:",config.KEYWORDS)
# time0=time.time()
# result = search(config.KEYWORDS)  
# time1=time.time()
# print(f"finish: cost {time1-time0: .2f} seconds")
# print(result) # 理想情况是List[str]
# print("length of output:",len(result))


SEARCH_INFORMATION_PROMPT = """
你要假装成为一个搜索引擎。根据用户给定的关键词，你需要：
1. 根据关键词编撰出一篇推文
2. 确保信息与用户的关键词相关
3. 推文中应当包含具体的细节，每次回答的结果相互独立

请直接进行输出：
"""

SAMPLE_INPUT = """
厦门旅游
"""

SAMPLE_OUTPUT = """
刚从厦门回来，整理了这份非典型游客指南。和先生带5岁娃的亲子游，全程公共交通，日均步数1.2万，适合喜欢深度体验的家庭参考：

🌇 ​​行程安排​​
Day1：沙坡尾艺术街区→顶澳仔猫街→钟鼓索道

10:00 沙坡尾旧厂房改造的艺术空间（免费）
推荐「反正」咖啡馆三楼露台，低消38元/人可拍双子塔全景
15:00 猫街博物馆二楼有20+猫咪常驻，孩子撸猫超开心
17:00 钟鼓索道建议选日落时段（提前3天预约）
Day2：鼓浪屿→八市海鲜市场

8:30 厦鼓码头→三丘田码头（35元/人）
重点走笔山路-鸡山路小众路线，避开旅行团人潮
14:00 龙山洞出口的「褚家园」老别墅咖啡值得停留
19:00 八市买海鲜加工推荐「阿玉」店，膏蟹75元/斤+15元加工费
Day3：环岛路骑行→黄厝海滩

租亲子电动车80元/天（曾厝垵站3号出口）
椰风寨到黄厝段人少景美，每隔1km有休息站
海滩挖沙工具租赁10元/套，建议自备防晒帽
🍜 ​​美食实测​​
▶ 四里沙茶面（湖滨店）：经典套餐22元，汤头浓郁
▶ 佳味再添小吃店：芋包5元/个，搭配甜辣酱很特别
▶ 思北花生汤：加蛋版本9元，温热清甜作夜宵刚好

⚠️ ​​避坑提醒​​

出租车司机推荐的「海上看金门」项目性价比低（198元/人，全程40分钟）
鼓浪屿上的「珍珠开蚌」体验店多为人工养殖珠
曾厝垵夜市同质化严重，更推荐去老城区开元路
这次总花费约3200元（两大一小），含高铁往返和民宿费用。大家觉得厦门哪个景点最值得二刷？求推荐其他小众玩法！

#厦门亲子游 #鼓浪屿攻略 #城市慢旅行
"""

def pesudo_crawl(keyword: str) -> List[Dict[str, Any]]:
    """
    使用大语言模型来伪装搜索引擎的搜索结果，用于测试时使用
    """
    llm = base_llm()
    messages = [
        SystemMessage(content=SEARCH_INFORMATION_PROMPT),
        HumanMessage(content=SAMPLE_INPUT),
        AIMessage(content=SAMPLE_OUTPUT),
        HumanMessage(content=keyword)
    ]
    result = llm.invoke(messages).content
    return [result]



