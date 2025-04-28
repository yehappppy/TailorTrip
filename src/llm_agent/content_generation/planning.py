from typing import Dict, Any, List
import json

from src.utils.util import get_logger, structure_output
from src.utils.llm import base_llm, cot_llm
from src.tools import crawl
from src.llm_agent.content_generation.prompt import (
    get_keyword_generation_messages,
    get_planning_messages
)

# 获取日志记录器
logger = get_logger("planning")

def generate_initial_keyword(user_description: str) -> str:
    """根据用户描述生成初始搜索关键词"""
    logger.info("生成初始搜索关键词")
    llm = base_llm()
    messages = get_keyword_generation_messages(user_description)
    response = llm.invoke(messages)
    keyword = response.content.strip()
    logger.info(f"生成的初始关键词: {keyword}")
    return keyword

def generate_search_plan(overview: str) -> Dict[str, Any]:
    """根据概览信息生成详细的搜索计划
    
    Args:
        overview: 概览信息文本，包含目的地的主要景点、美食、交通等信息
        
    Returns:
        Dict[str, Any]: 包含以下键的字典：
            - "thinking_process": 规划思路说明
            - "search_plan": 进行搜索获取信息的计划
            - "keywords": 所有需要搜索的关键词列表
    """
    logger.info("开始生成详细的搜索计划")
    
    # 使用cot_llm进行复杂的规划任务
    llm = base_llm()
    messages = get_planning_messages(overview)

    response = llm.invoke(messages)
    
    try:
        # 解析响应JSON
        plan_data = structure_output(response.content)
        
        # 构建返回结果
        result = {
            "thinking_process": plan_data['thinking_process'],
            "search_plan": plan_data['search_plan'],
            "keywords": plan_data['keywords']
        }
        
        logger.info(f"生成了{len(result['keywords'])}个搜索关键词")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"解析计划JSON失败: {e}")
        raise
    except KeyError as e:
        logger.error(f"计划数据结构不完整: {e}")
        raise

def planning(user_description: str) -> Dict[str, Any]:
    """
    根据用户描述生成详细的搜索计划
    
    Args:
        user_description: 用户的描述文本
        
    Returns:
        Dict[str, Any]: 包含以下键的字典
            - "thinking_process": 规划思路说明
            - "itinerary": 每天的行程安排列表
            - "keywords": 所有需要搜索的关键词列表
    """
    logger.info(f"开始生成详细的搜索计划，用户描述: {user_description}")
    
    # 步骤1：生成概览信息
    keyword = generate_initial_keyword(user_description)
    
    # 步骤2：用keyword调用crawl.py中的crawl进行搜索
    search_result = crawl(keyword)[0]
    
    # 步骤3：生成详细的搜索计划
    plan_data = generate_search_plan(search_result)
    
    logger.info("搜索计划生成完成")
    return plan_data