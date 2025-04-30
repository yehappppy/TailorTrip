# Entry point for new_planner
import json
import sys
import time
import argparse
from src.llm_agent.new_planner.workflow import generate_plan

def main():
    """主函数，处理命令行参数并执行规划生成"""
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='生成分层旅游规划')
    parser.add_argument('query', nargs='?', default='香港旅游', help='用户查询或需求描述')
    parser.add_argument('--max-depth', type=int, default=3, help='最大深度限制，同时控制递归轮数和树高度，默认为3')
    args = parser.parse_args()
    
    user_input = args.query
    max_depth = args.max_depth
    
    if user_input == '云南旅游':
        print(f"未提供输入参数，使用默认值: '{user_input}'")
    
    print(f"\n[1/3] 开始处理用户输入: '{user_input}'")
    print(f"      最大深度限制: {max_depth}")
    
    # 生成规划
    start_time = time.time()
    result = generate_plan(user_input, max_depth)
    end_time = time.time()
    
    print(f"\n[2/3] 规划生成完成! 耗时: {end_time - start_time:.2f}秒")
    print(f"      关键词: {result.get('keyword')}")
    
    # 获取规划JSON
    plan = result.get('plan', {})
    
    # 打印规划JSON
    print(f"\n[3/3] 输出最终规划JSON:")
    print("-" * 50)
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    print("-" * 50)
    
    return result

if __name__ == "__main__":
    main()
