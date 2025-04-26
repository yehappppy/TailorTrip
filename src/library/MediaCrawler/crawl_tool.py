# version2:
import subprocess 
import os
import json
from datetime import datetime

# 定义一个简单的 @tool 装饰器
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
def search(keyword: str) -> str:
    """
    A tool function to execute a search using the specified keyword and process the JSON results.
    
    Args:
        keyword (str): The search keyword.
    
    Returns:
        str: A formatted string containing the extracted information.
    """
    try:
        # 调用命令行工具并传入参数
        subprocess.run(
            [
                "python", "main.py", 
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
        content_json_path = rf"./data/xhs/json/search_contents_{current_date}.json"
        comments_json_path = rf"./data/xhs/json/search_comments_{current_date}.json"
        images_folder_path = rf"./data/xhs/images"
        output_txt_path = rf"./output_test.txt"
        
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
        for content in filtered_contents:
            note_id = content["note_id"]
            title = content["title"]
            desc = content["desc"]
            
            # 写标题
            output_lines.append(f"标题：{title}")
            
            # 写内容
            output_lines.append("内容：")
            output_lines.append(f"{desc}")
            
            # 写评论
            output_lines.append("评论：")
            if note_id in comments_by_note_id:
                for comment in comments_by_note_id[note_id]:
                    output_lines.append(comment)
            else:
                output_lines.append("暂无评论")
            
            # 写OCR识别结果
            output_lines.append("OCR识别结果：")
            note_folder_path = os.path.join(images_folder_path, note_id)
            if os.path.exists(note_folder_path):
                for txt_file in os.listdir(note_folder_path):
                    if txt_file.endswith(".txt"):
                        txt_file_path = os.path.join(note_folder_path, txt_file)
                        with open(txt_file_path, 'r', encoding='utf-8') as tf:
                            ocr_content = tf.read()
                            output_lines.append(ocr_content)
            else:
                output_lines.append("暂无OCR识别结果")
            
            # 添加分隔符
            output_lines.append("\n" + "="*50 + "\n")
        
        # 将所有内容写入文件并返回字符串
        with open(output_txt_path, 'w', encoding='utf-8') as output_file:
            output_file.write("\n".join(output_lines))
        
        return "\n".join(output_lines)
    
    except subprocess.CalledProcessError as e:
        # 捕获错误并返回错误信息
        return f"Error: {e.stderr.strip()}"
    except FileNotFoundError as e:
        return f"Error: File not found - {e}"
    except json.JSONDecodeError as e:
        return f"Error: Failed to decode JSON - {e}"
    


### 示例调用：
import time
from config.base_config import KEYWORDS

time0=time.time()
KEYWORDS = "曾母暗沙旅游"
result = search(KEYWORDS)
time1=time.time()
print(f"finish: cost {time1-time0: .2f} seconds")
print(result)