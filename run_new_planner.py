# Entry point for new_planner
from src.llm_agent.new_planner import generate_plan

if __name__ == "__main__":
    # 用户输入
    user_input = "云南旅游"
    
    # 生成规划
    result = generate_plan(user_input)
    
    # 打印结果
    print(f"\n>>> 关键词: {result.get('keyword')}")
    
    plan = result.get('plan', {})
    if plan:
        print(f">>> 计划包含实体: {plan.get('entity', '未知')}")
        
        children = plan.get('children', [])
        print(f">>> 子实体数量: {len(children)}")
        
        if children:
            print(f">>> 子实体: {', '.join([child.get('entity', '未知') for child in children])}")

    
    print("\n--- 最终规划结果 ---")
    
    import json
    print(json.dumps(plan, ensure_ascii=False, indent=2))
