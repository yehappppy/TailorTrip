from typing import Dict, Any, List
from src.utils.util import get_logger
from src.llm_agent.content_generation.planning import planning
from src.llm_agent.content_generation.recursive_searching import recursive_searching

logger = get_logger("content_generation")

def generate_travel_plan(user_description: str, max_depth: int = 3) -> Dict[str, Any]:
    """
    根据用户描述生成旅行计划的主入口函数
    
    Args:
        user_description: 用户的旅行需求描述
        max_depth: 递归搜索的最大深度，默认为3
        
    Returns:
        Dict[str, Any]: 包含以下键的字典：
            - "tree": 搜索树的JSON字符串
            - "content": 生成的旅行建议内容
            - "plan": 详细的旅行计划
            - "keywords": 搜索关键词列表
    """
    logger.info(f"开始为用户生成旅行计划，输入描述：{user_description}")
    
    # 步骤1：生成详细的搜索计划
    search_plan = planning(user_description)

    print(search_plan)
    
    logger.info(f"搜索计划生成完毕，开始细节搜索")

    # 步骤2：执行递归搜索
    # search_result = recursive_searching(user_description, max_depth)
    
    logger.info(f"细节搜索完成，开始生成最终回答")

    # 步骤3：构建返回结果
    result = {
        "tree": search_result["tree"],
        "content": search_result["content"],
    }
    
    logger.info("旅行计划生成完成")
    return result

def main():
    """测试用的主函数"""
    # 测试用例
    test_description = "我想去一个有美丽海滩和美食的地方度假，预算适中，最好有一些文化体验"
    result = generate_travel_plan(test_description)
    
    print("\n=== 生成的旅行计划 ===")
    print(f"搜索关键词：{result['keywords']}")
    print("\n规划思路：")
    print(result['thinking_process'])
    print("\n旅行安排：")
    for day in result['plan']:
        print(f"\n{day['天数']}:")
        for activity in day['行程']:
            print(f"  {activity['时间']} - {activity['活动']} ({activity['搜索关键词']})")
    print("\n最终建议：")
    print(result['content'])

if __name__ == "__main__":
    main()
