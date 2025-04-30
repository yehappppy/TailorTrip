import json
import time
import argparse
import time

# 添加测试标记
__test__ = True

from src.llm_agent.run import generate_travel_plan
from src.utils.util import get_logger

logger = get_logger("test_agent")

def main():
    """主函数，测试llm_agent的功能"""
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='测试llm_agent的功能')
    parser.add_argument('query', nargs='?', default='云南有什么好玩的地方？', help='用户查询或需求描述')
    args = parser.parse_args()
    
    user_input = args.query
    chat_history = []  # 可以添加聊天历史进行测试
    
    print(f"\n[1/3] 开始处理用户输入: '{user_input}'")
    
    # 生成规划
    start_time = time.time()
    result = generate_travel_plan(user_input, chat_history)
    end_time = time.time()
    
    print(f"\n[2/3] 处理完成! 耗时: {end_time - start_time:.2f}秒")
    print(f"      状态: {result.get('status')}")
    if result.get('status') == 'confirmed':
        print(f"      补全后的查询: {result.get('final_query')}")
        print(f"      查询类型: {result.get('flag')}（{result.get('reason')}）")
        print(f"      用户偏好: {json.dumps(result.get('preference'), ensure_ascii=False)}")
    
    # 打印结果
    print(f"\n[3/3] 输出结果:")
    print("-" * 50)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("-" * 50)
    
    return result

def test_cases():
    """测试不同类型的用户输入"""
    test_inputs = [
        # 递归规划类查询
        "我想去云南玩，帮我规划一下",
        # 搜索类查询
        "昆明有什么好玩的",
        # 简单问答类查询
        "丽江古城门票多少钱",
        # 需要补全的查询
        "想去玩，有什么推荐的",
        # 特殊情况
        "。。。"
    ]
    
    print("\n开始运行测试用例...")
    print("-" * 50)
    
    for i, test_input in enumerate(test_inputs, 1):
        print(f"\n测试用例 {i}: '{test_input}'")
        try:
            result = generate_travel_plan(test_input)
            print(f"状态: {result.get('status')}")
            if result.get('status') == 'confirmed':
                print(f"补全后的查询: {result.get('final_query')}")
            print(f"结果类型: {type(result.get('result'))}")
        except Exception as e:
            print(f"错误: {str(e)}")
        print("-" * 30)
    
    print("\n测试用例运行完成")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_cases()
    else:
        main()
