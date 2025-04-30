from typing import Dict, Any, List
import json
import re
import copy
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from src.utils.llm import base_llm
from src.utils.util import get_logger, structure_output
from src.tools.crawl import pesudo_crawl

logger = get_logger("content_generation.planning")



# 初始规划生成提示词
INITIAL_PLAN_PROMPT = """
请为给定的关键词创建一个初始规划节点。返回一个JSON对象，包含以下字段：
- entity（实体名称，就是给定的关键词）
- information（空字符串，空信息）
- children（空数组，表示没有子节点）
- is_complete（false，表示该节点信息不完整）

只需返回JSON对象，不需要额外解释。
"""

INITIAL_PLAN_SAMPLE_INPUT = "云南旅游"
INITIAL_PLAN_SAMPLE_OUTPUT = """
{
  "entity": "云南旅游",
  "information": "",
  "is_complete": false,
  "children": []
}
"""

def get_initial_plan_messages(keyword: str) -> List:
    """
    构建初始规划的消息列表
    
    Args:
        keyword: 关键词
        
    Returns:
        List: 包含系统提示、示例和关键词的消息列表
    """
    
    return [
        SystemMessage(content=INITIAL_PLAN_PROMPT),
        HumanMessage(content=INITIAL_PLAN_SAMPLE_INPUT),
        AIMessage(content=INITIAL_PLAN_SAMPLE_OUTPUT),
        HumanMessage(content=keyword)
    ]

def create_initial_plan(keyword: str) -> Dict[str, Any]:
    """
    为关键词创建初始规划节点
    
    Args:
        keyword: 关键词
        
    Returns:
        Dict[str, Any]: 初始规划节点
    """
    # 使用LLM创建初始规划节点
    messages = get_initial_plan_messages(keyword)
    llm = base_llm()
    response = llm.invoke(messages)
    
    # 解析规划JSON
    plan = structure_output(response.content)
    if plan is None:
        plan = {}
    
    # 如果解析失败，创建一个默认的初始节点
    if not plan:
        plan = {
            "entity": keyword,
            "information": "",
            "is_complete": False,
            "children": []
        }
    
    return plan

def search_entity_info(entity: str) -> List[str]:
    """
    搜索实体相关的信息
    
    Args:
        entity: 实体名称
        
    Returns:
        List[str]: 搜索结果列表
    """
    try:
        return pesudo_crawl.invoke(entity)
    except AttributeError:
        # 兼容旧版本
        logger.warning("pesudo_crawl 使用了已弃用的 __call__ 方法，将在未来版本中移除")
        return pesudo_crawl(entity)

def update_plan_with_info(plan: Dict[str, Any], search_results: List[str]) -> Dict[str, Any]:
    """
    使用搜索结果直接更新规划节点
    
    Args:
        plan: 当前规划节点
        search_results: 搜索结果列表
        
    Returns:
        Dict[str, Any]: 更新后的规划节点
    """
    # 创建规划节点的副本，避免修改原始节点
    updated_plan = copy.deepcopy(plan)
    
    # 将搜索结果合并为一个字符串
    info_text = "\n".join(search_results) if isinstance(search_results, list) else str(search_results)
    
    # 直接更新节点的information字段
    updated_plan["information"] = info_text
    
    # 确保其他必要字段存在
    if "entity" not in updated_plan:
        updated_plan["entity"] = plan.get("entity", "")
    if "is_complete" not in updated_plan:
        updated_plan["is_complete"] = False
    if "children" not in updated_plan:
        updated_plan["children"] = []
    
    logger.info(f"直接更新节点 '{updated_plan['entity']}' 的信息，长度: {len(info_text)} 字符")
    
    return updated_plan
