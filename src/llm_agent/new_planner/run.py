from typing import Dict, Any, List
from src.utils.util import get_logger
from src.llm_agent.new_planner.keyword_extraction import extract_keyword
from src.llm_agent.new_planner.planning import generate_initial_plan
from src.llm_agent.new_planner.recursive_searching import recursive_search

logger = get_logger("new_planner")

def generate_plan(user_input: str, max_depth: int = 3) -> Dict[str, Any]:
    """
    根据用户输入生成分层规划的主入口函数
    
    Args:
        user_input: 用户输入的查询或需求描述
        max_depth: 递归搜索的最大深度，默认为3
        
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
    
    # 步骤2：生成初始规划
    initial_plan = generate_initial_plan(keyword)
    logger.info(f"初始规划生成完成")
    print(f">>> 初始规划生成完成")
    
    # 打印初始规划信息
    initial_plan_data = initial_plan.get("plan", {})
    if initial_plan_data:
        print(f">>> 初始规划主实体: {initial_plan_data.get('entity', '未知')}")
        initial_children = initial_plan_data.get('children', [])
        print(f">>> 初始子实体数量: {len(initial_children)}")
        if initial_children:
            print(f">>> 初始子实体: {', '.join([child.get('entity', '未知') for child in initial_children])}")
    
    # 步骤3：执行递归搜索和规划更新
    print("\n>>> 开始执行递归搜索和规划更新...")
    final_result = recursive_search(initial_plan, max_depth)
    logger.info(f"递归搜索和规划更新完成")
    print(f">>> 递归搜索和规划更新完成")
    
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

def main():
    """测试用的主函数"""
    # 测试用例
    test_input = "云南旅游"
    result = generate_plan(test_input)
    
    print("\n=== 生成的分层规划 ===")
    print(f"关键词：{result['keyword']}")
    
    plan = result.get('plan', {})
    if plan:
        print(f"\n主实体：{plan.get('entity', '未知')}")
        children = plan.get('children', [])
        print(f"子实体数量：{len(children)}")
        if children:
            print(f"子实体：{', '.join([child.get('entity', '未知') for child in children])}")
    
    print("\n最终规划结果：")
    import json
    print(json.dumps(plan, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
