"""
生成最终的综合回答
"""
import json
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from src.utils.llm import cot_llm

def generate_recursive_answer(query: str, plan: Dict) -> str:
    """
    根据递归规划结果生成综合回答
    
    Args:
        query: 用户查询
        plan: 规划结果
        
    Returns:
        str: 综合回答
    """
    messages = [
        SystemMessage(content="你是一个旅游规划助手。根据用户查询和规划结果，生成一个综合的、有组织的旅游建议。回答应该简洁明了，使用Markdown格式。"),
        HumanMessage(content=f"""用户查询：{query}

规划结果：{json.dumps(plan, ensure_ascii=False, indent=2)}

请生成一个综合的旅游建议。""")
    ]
    
    llm = cot_llm()
    response = llm.invoke(messages)
    return response.content

def generate_search_answer(query: str, entities: List, reasoning: str) -> str:
    """
    根据搜索结果生成综合回答
    
    Args:
        query: 用户查询
        entities: 搜索到的实体列表
        reasoning: 实体选择原因
        
    Returns:
        str: 综合回答
    """
    messages = [
        SystemMessage(content="你是一个旅游信息助手。根据用户查询和搜索结果，生成一个综合的、有组织的回答。回答应该简洁明了，使用Markdown格式。"),
        HumanMessage(content=f"""用户查询：{query}

搜索到的实体：{json.dumps(entities, ensure_ascii=False, indent=2)}
实体选择原因：{reasoning}

请生成一个综合的回答。""")
    ]
    
    llm = cot_llm()
    response = llm.invoke(messages)
    return response.content
