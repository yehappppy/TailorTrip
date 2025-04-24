from typing import List, Dict, Any, Optional
import json

from src.utils.util import get_logger
from src.tools.crawl import search_information
from src.utils.llm import base_llm, cot_llm
from src.llm_agent.content_generation.tree import SearchNode, SearchTree
from src.llm_agent.content_generation.prompt import (
    get_keyword_generation_messages,
    get_keyword_extraction_messages,
    get_result_evaluation_messages,
    get_final_response_messages
)

# 获取日志记录器
logger = get_logger("recursive_searching")


def generate_initial_keyword(user_description: str) -> str:
    """根据用户描述生成初始搜索关键词"""
    logger.info("生成初始搜索关键词")
    llm = base_llm()
    messages = get_keyword_generation_messages(user_description)
    response = llm.invoke(messages)
    keyword = response.content.strip()
    logger.info(f"生成的初始关键词: {keyword}")
    return keyword


def is_specific_location(search_result: str) -> bool:
    """判断搜索结果是否包含关于特定地点的信息"""
    logger.info("评估搜索结果是否包含特定地点信息")
    llm = base_llm()
    messages = get_result_evaluation_messages(search_result)
    response = llm.invoke(messages)
    result = response.content.strip().lower() in ["yes", "是"]
    logger.info(f"评估结果: {'是特定地点' if result else '不是特定地点'}")
    return result


def generate_final_response(tree: SearchTree, user_input: str) -> str:
    """根据搜索树和用户原始输入生成最终的综合回答
    Args:
        tree: 完整的搜索树，包含所有搜索结果
        user_input: 用户的原始输入描述
    Returns:
        str: 生成的最终答案
    """
    logger.info("开始生成最终回答")
    llm = cot_llm()
    
    # 将搜索树转换为JSON格式
    tree_json = json.dumps(tree.to_dict(), ensure_ascii=False, indent=2)
    
    messages = get_final_response_messages(user_input, tree_json)
    response = llm.invoke(messages)
    logger.info("已生成最终回答")
    return response.content.strip()


def extract_keywords(search_result: str) -> List[str]:
    """从搜索结果中提取重要关键词用于进一步搜索"""
    logger.info("从搜索结果中提取关键词")
    llm = base_llm()
    messages = get_keyword_extraction_messages(search_result)
    response = llm.invoke(messages)
    keywords = [keyword.strip() for keyword in response.content.split(",")]
    logger.info(f"提取的关键词: {keywords}")
    return keywords


def search_with_keyword(keyword: str) -> str:
    """使用给定关键词，调用搜索引擎执行搜索"""
    logger.info(f"使用关键词搜索: {keyword}")
    results = search_information(keyword)
    if results and isinstance(results, list) and len(results) > 0:
        # 如果返回多个结果，只返回第一个
        result = results[0] if isinstance(results[0], str) else results[0]
        logger.debug(f"搜索结果: {result[:100]}...")  # 只记录前100个字符
        return result
    logger.warning(f"关键词 '{keyword}' 没有返回搜索结果")
    return ""


def build_search_tree(keyword: str, current_depth: int, max_depth: int) -> SearchNode:
    """递归构建搜索树
    
    Args:
        keyword: 当前节点的搜索关键词
        current_depth: 当前深度（从1开始）
        max_depth: 最大搜索深度
        
    Returns:
        SearchNode: 构建好的搜索树节点
    """
    logger.info(f"构建搜索树，深度: {current_depth}/{max_depth}，关键词: {keyword}")
    
    # 执行搜索
    search_result = search_with_keyword(keyword)
    
    # 判断是否包含具体地点信息
    is_specific = is_specific_location(search_result)
    
    # 创建当前节点
    current_node = SearchNode(
        keyword=keyword,
        content=search_result,
        is_specific=is_specific
    )
    
    # 如果达到最大深度或已找到具体地点，则停止递归
    if current_depth >= max_depth or is_specific:
        return current_node
    
    # 从搜索结果中提取新的关键词
    new_keywords = extract_keywords(search_result)
    
    # 递归构建子树
    children = []
    for new_keyword in new_keywords:
        child_node = build_search_tree(new_keyword, current_depth + 1, max_depth)
        children.append(child_node)
    
    # 将子节点添加到当前节点
    for child in children:
        current_node.add_child(child)
    
    return current_node


def recursive_searching(user_description: str, max_depth: int = 3) -> Dict[str, str]:
    """根据用户描述执行递归搜索并返回结果字典
    
    Args:
        user_description: 用户的描述文本
        max_depth: 最大搜索深度（从1开始计数）
    
    Returns:
        Dict[str, str]: 包含两个键的字典
            - "tree": 搜索树的JSON字符串
            - "content": 基于搜索树生成的最终回答
    """
    logger.info(f"开始递归搜索，用户描述: {user_description}")
    
    # 步骤0：生成初始搜索关键词
    initial_keyword = generate_initial_keyword(user_description)
    
    # 步骤1-3：递归构建搜索树（从深度1开始）
    root_node = build_search_tree(initial_keyword, 1, max_depth)
    
    # 创建搜索树对象
    search_tree = SearchTree(root=root_node)
    
    # 生成最终回答
    final_response = generate_final_response(search_tree, user_description)
    
    # 构建返回结果
    result = {
        "tree": search_tree.to_json(),
        "content": final_response
    }
    
    logger.info("递归搜索完成")
    logger.debug(f"树的大小: {len(result['tree'])} 字符")
    logger.debug(f"生成内容大小: {len(result['content'])} 字符")
    
    return result
