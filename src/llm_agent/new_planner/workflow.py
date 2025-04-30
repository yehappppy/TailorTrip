# 新版规划器的工作流定义和核心功能
from typing import Dict, Any, List
from src.utils.util import get_logger
from src.llm_agent.new_planner.keyword_extraction import extract_keyword
from src.llm_agent.new_planner.planning import create_initial_plan
from src.llm_agent.new_planner.recursive_searching import recursive_search
from src.tools.crawl import pesudo_crawl

logger = get_logger("new_planner.workflow")

def generate_plan(user_input: str, max_depth: int = 3) -> Dict[str, Any]:
    """
    根据用户输入生成分层规划的主入口函数
    
    Args:
        user_input: 用户输入的查询或需求描述
        max_depth: 最大深度限制，同时控制递归轮数和树高度，默认为3
        
    Returns:
        Dict[str, Any]: 包含以下键的字典：
            - "keyword": 提取的主关键词
            - "references": 搜索参考信息
            - "plan": 分层规划结果
    """
    logger.info(f"开始为用户生成分层规划，输入：{user_input}")
    
    # 步骤1：提取关键词
    keyword = extract_keyword(user_input)
    logger.info(f"关键词提取完成：{keyword}")
    print(f">>> 提取的关键词: {keyword}")
    
    # 步骤2：创建初始规划节点
    initial_plan = create_initial_plan(keyword)
    logger.info(f"初始规划节点创建完成")
    print(f">>> 初始规划节点创建完成")
    
    # 步骤3：获取初始参考信息
    try:
        references = pesudo_crawl.invoke(keyword)
    except AttributeError:
        references = pesudo_crawl(keyword)
    
    # 创建初始结果对象
    initial_result = {
        "references": references,
        "plan": initial_plan
    }
    
    # 步骤4：执行递归规划
    print(">>> 开始执行递归规划...")
    final_result = recursive_search(initial_result, max_depth)
    logger.info(f"递归规划完成")
    print(f">>> 递归规划完成")
    
    # 构建返回结果
    result = {
        "keyword": keyword,
        "references": final_result.get("references", []),
        "plan": final_result.get("plan", {})
    }
    
    # 打印参考信息数量
    print(f">>> 收集的参考信息数量: {len(result['references'])}")
    
    logger.info("分层规划生成完成")
    return result
