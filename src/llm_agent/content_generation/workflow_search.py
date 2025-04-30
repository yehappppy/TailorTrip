from typing import Dict, Any, List
import json
from langchain_core.messages import SystemMessage, HumanMessage
from src.utils.util import get_logger
from src.utils.llm import cot_llm
from src.llm_agent.content_generation.keyword_extraction import extract_keyword, extract_initial_entities
from src.tools.crawl import pesudo_crawl

logger = get_logger("content_generation.search_workflow")

def generate_search_result(final_query: str, user_preference: Dict) -> Dict[str, Any]:
    """
    根据用户查询生成搜索结果
    
    Args:
        final_query: 经过意图理解后的用户查询
        user_preference: 用户偏好字典
        
    Returns:
        Dict[str, Any]: 包含以下键的字典：
            - "keyword": 提取的主关键词
            - "references": 搜索参考信息
            - "entities": 提取的实体列表
            - "reasoning": 实体选择原因
    """
    # 1. 提取关键词
    keyword = extract_keyword(final_query)
    logger.info(f"提取到主关键词: {keyword}")
    
    # 2. 搜索参考资料
    references = pesudo_crawl(keyword)
    logger.info(f"获取到参考资料数量: {len(references)}")
    
    # 3. 根据用户偏好提取初始实体
    extraction_result = extract_initial_entities(references, user_preference)
    entities = extraction_result.get("entities", [])
    reasoning = extraction_result.get("reasoning", "")
    
    logger.info(f"提取到实体: {entities}")
    logger.info(f"实体选择原因: {reasoning}")
    
    # 构建基础结果
    result = {
        "keyword": keyword,
        "references": references,
        "entities": entities,
        "reasoning": reasoning
    }
    
    # 生成最终的综合回答
    from .answer_generation import generate_search_answer
    result["answer"] = generate_search_answer(final_query, entities, reasoning)
    
    # 打印综合回答
    print("\n>>> 综合回答:")
    print("-" * 50)
    print(result["answer"])
    print("-" * 50)
    
    return result
