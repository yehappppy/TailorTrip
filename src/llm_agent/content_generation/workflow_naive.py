from typing import Dict, Any
from src.utils.util import get_logger
from src.utils.llm import cot_llm
from langchain_core.messages import SystemMessage, HumanMessage

logger = get_logger("content_generation.naive_workflow")

NAIVE_PROMPT = """
你是一个旅游咨询助手。请根据用户的查询，直接给出简洁的回答。
回答要求：
1. 内容要准确、客观
2. 语言要简洁、清晰
3. 如果是具体问题，直接给出答案
4. 如果是开放性问题，给出2-3点建议

请直接回答，不要解释你的角色。
"""

def generate_naive_answer(final_query: str) -> Dict[str, Any]:
    """
    直接回答用户查询
    
    Args:
        final_query: 经过意图理解后的用户查询
        
    Returns:
        Dict[str, Any]: 包含以下键的字典：
            - "answer": 生成的回答
    """
    messages = [
        SystemMessage(content=NAIVE_PROMPT),
        HumanMessage(content=final_query)
    ]
    
    llm = cot_llm()
    response = llm.invoke(messages)
    answer = response.content.strip()
    
    logger.info(f"生成回答: {answer}")
    
    return {
        "answer": answer
    }
