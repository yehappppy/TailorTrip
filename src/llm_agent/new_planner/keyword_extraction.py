from typing import List
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from src.utils.llm import fast_llm

# 关键词提取提示模板
KEYWORD_EXTRACTION_PROMPT = """
请根据用户输入，提取一个最相关且唯一的关键词。
只需返回关键词本身，不要额外解释。
"""

# 示例输入输出
KEYWORD_EXTRACTION_SAMPLE_INPUT = "我想了解巴黎的著名景点和历史。"
KEYWORD_EXTRACTION_SAMPLE_OUTPUT = "巴黎景点"

def get_keyword_extraction_messages(user_input: str) -> List:
    """
    构建关键词提取的消息列表
    
    Args:
        user_input: 用户输入的查询或需求描述
        
    Returns:
        List: 包含系统提示、示例和用户输入的消息列表
    """
    return [
        SystemMessage(content=KEYWORD_EXTRACTION_PROMPT),
        HumanMessage(content=KEYWORD_EXTRACTION_SAMPLE_INPUT),
        AIMessage(content=KEYWORD_EXTRACTION_SAMPLE_OUTPUT),
        HumanMessage(content=f"用户输入: {user_input}")
    ]

def extract_keyword(user_input: str) -> str:
    """
    从用户输入中提取关键词
    
    Args:
        user_input: 用户输入的查询或需求描述
        
    Returns:
        str: 提取的关键词
    """
    messages = get_keyword_extraction_messages(user_input)
    llm = fast_llm()
    response = llm.invoke(messages)
    
    # 清理LLM响应，提取纯关键词
    keyword = response.content.strip()
    keyword = keyword.replace('关键词：', '').replace('关键词:', '')
    keyword = keyword.replace('"', '').replace('"','').replace('"','')
    
    return keyword
