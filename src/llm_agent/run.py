from typing import Dict, Any, List

from src.llm_agent.user_intention.user_intention import process_user_input
from src.llm_agent.content_generation.workflow_recursive import generate_recursive_plan
from src.llm_agent.content_generation.workflow_search import generate_search_result
from src.llm_agent.content_generation.workflow_naive import generate_naive_answer
from src.utils.util import get_logger

logger = get_logger("llm_agent.run")

def generate_travel_plan(user_input: str, chat_history: List = None) -> Dict[str, Any]:
    """
    处理用户输入并生成旅游规划的主入口函数
    
    Args:
        user_input: 用户原始输入
        chat_history: 聊天历史记录，用于上下文理解
        
    Returns:
        Dict[str, Any]: 包含以下键的字典：
            - status: 处理状态，confirmed/unconfirmed
            - original: 原始输入
            - final_query: 补全后的查询（如果status为confirmed）
            - result: 根据不同flag生成的结果
    """
    if chat_history is None:
        chat_history = []
        
    # 1. 处理用户意图
    intention_result = process_user_input(user_input, chat_history)
    
    if intention_result["status"] != "confirmed":
        return intention_result
    
    # 2. 根据flag选择不同的处理流程
    final_query = intention_result["final_query"]
    flag = intention_result["flag"]
    preference = intention_result.get("preference", {})
    
    logger.info(f"处理用户查询: {final_query}")
    logger.info(f"意图类型: {flag}")
    logger.info(f"用户偏好: {preference}")
    
    # 3. 根据不同flag执行不同的处理流程
    if flag == "C":
        result = generate_recursive_plan(final_query, preference)
    elif flag == "B":
        result = generate_search_result(final_query, preference)
    else:  # naive
        result = generate_naive_answer(final_query)
        
    # 4. 返回结果
    response = {
        "status": intention_result["status"],
        "original": intention_result["original"]
    }
    
    # 如果状态是confirmed，添加其他字段
    if intention_result["status"] == "confirmed":
        response.update({
            "final_query": intention_result["final_query"],
            "flag": intention_result["flag"],
            "reason": intention_result["reason"],
            "preference": intention_result["preference"],
            "result": result
        })
    # 如果状态是blocked，添加原因
    elif intention_result["status"] == "blocked":
        response["reason"] = intention_result["reason"]
        
    return response
