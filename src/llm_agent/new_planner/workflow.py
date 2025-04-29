# Langgraph workflow definition for new_planner
from langgraph.graph import StateGraph, END
from src.llm_agent.new_planner.nodes import (
    extract_initial_keyword,
    init_search_reference,
    init_summarize_plan,
    recursive_search_reference,
    recursive_summarize_plan,
    check_all_visited
)
from src.llm_agent.new_planner.state import PlannerState

def build_workflow():
    # 创建主工作流
    workflow = StateGraph(PlannerState)
    
    # 添加所有节点
    workflow.add_node("extract_initial_keyword", extract_initial_keyword)
    workflow.add_node("init_search_reference", init_search_reference)
    workflow.add_node("init_summarize_plan", init_summarize_plan)
    workflow.add_node("recursive_search_reference", recursive_search_reference)
    workflow.add_node("recursive_summarize_plan", recursive_summarize_plan)
    workflow.add_node("check_all_visited", check_all_visited)
    
    # 设置入口节点
    workflow.set_entry_point("extract_initial_keyword")
    
    # 初始规划部分的边
    workflow.add_edge("extract_initial_keyword", "init_search_reference")
    workflow.add_edge("init_search_reference", "init_summarize_plan")
    workflow.add_edge("init_summarize_plan", "recursive_search_reference")
    
    # 递归搜索部分的边
    workflow.add_edge("recursive_search_reference", "recursive_summarize_plan")
    workflow.add_edge("recursive_summarize_plan", "check_all_visited")
    
    # 条件边：根据check_all_visited函数的返回值决定下一步
    workflow.add_conditional_edges(
        "check_all_visited",
        check_all_visited,
        {
            "recursive_search_reference": "recursive_search_reference"
            # 当返回"return"时，自动结束
        }
    )
    
    # 编译工作流
    return workflow.compile()
