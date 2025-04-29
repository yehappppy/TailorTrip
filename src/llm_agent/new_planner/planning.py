from typing import Dict, Any, List
import json
import re
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from src.utils.llm import base_llm

# 导入 src.tools.crawl 中的 pesudo_crawl 函数
from src.tools.crawl import pesudo_crawl

def search_reference(keyword: str) -> List[str]:
    """
    搜索关键词相关的参考信息
    
    Args:
        keyword: 搜索关键词
        
    Returns:
        List[str]: 搜索结果列表
    """
    # 使用 pesudo_crawl 函数获取搜索结果
    # 使用 invoke 方法代替 __call__
    try:
        return pesudo_crawl.invoke(keyword)
    except AttributeError:
        # 兼容旧版本
        print("[警告] pesudo_crawl 使用了已弃用的 __call__ 方法，将在未来版本中移除")
        return pesudo_crawl(keyword)

# 从 prompts.py 导入提示词模板
from src.llm_agent.new_planner.prompts import get_plan_generation_messages

def parse_plan_json(content: str) -> Dict[str, Any]:
    """
    解析LLM生成的规划JSON
    
    Args:
        content: LLM生成的内容
        
    Returns:
        Dict[str, Any]: 解析后的规划字典
    """
    try:
        # 尝试直接解析JSON
        return json.loads(content)
    except Exception:
        # 回退方案：尝试提取大括号内的内容
        match = re.search(r'\{[\s\S]*\}', content)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        # 如果都失败，返回空字典
        return {}

def generate_initial_plan(keyword: str) -> Dict[str, Any]:
    """
    生成初始规划
    
    Args:
        keyword: 搜索关键词
        
    Returns:
        Dict[str, Any]: 包含初始规划和参考信息的字典
    """
    print("\n" + "-"*50)
    print(f"[生成初始规划] 关键词: {keyword}")
    
    # 搜索参考信息
    references = search_reference(keyword)
    print(f"[参考信息] 数量: {len(references)}")
    
    # 生成初始规划
    messages = get_plan_generation_messages("，".join(references))
    llm = base_llm()
    response = llm.invoke(messages)
    
    # 解析规划JSON
    plan = parse_plan_json(response.content)
    print("[初始规划JSON] 生成完成")
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    print("-"*50)
    
    return {
        "references": references,
        "plan": plan
    }
