# new_planner 的 langgraph workflow 节点实现
from typing import Dict, Any, List
from src.llm_agent.new_planner.prompts import get_keyword_generation_messages, get_summarize_plan_messages
from src.llm_agent.new_planner.state import PlannerState

# utils.pesudo_crawl 占位符
try:
    from utils import pesudo_crawl
except ImportError:
    def pesudo_crawl(keyword: str):
        # 伪造爬虫结果
        return [f"{keyword} 的搜索结果"]

# ===== init_planning 子图节点 =====
def extract_initial_keyword(state: PlannerState) -> PlannerState:
    """从用户输入中提取唯一关键词，调用LLM。"""
    from src.utils.llm import fast_llm
    messages = get_keyword_generation_messages(state["user_input"])
    llm = fast_llm()
    response = llm.invoke(messages)
    keyword = response.content.strip().replace('关键词：', '').replace('关键词:', '').replace('"', '').replace('“','').replace('”','')
    return {**state, "keyword": keyword}

def init_search_reference(state: PlannerState) -> PlannerState:
    """首次搜索，获取初始参考信息。"""
    results = pesudo_crawl(state["keyword"])
    return {**state, "references": results}

def init_summarize_plan(state: PlannerState) -> PlannerState:
    """根据初次搜索结果生成初始plan json，调用LLM。"""
    import json
    from src.utils.llm import base_llm
    references = state.get("references", [])
    messages = get_summarize_plan_messages("，".join(references))
    llm = base_llm()
    response = llm.invoke(messages)
    try:
        plan = json.loads(response.content)
    except Exception:
        # fallback: 尝试找出大括号内容
        import re
        match = re.search(r'\{[\s\S]*\}', response.content)
        plan = json.loads(match.group()) if match else {}
    return {**state, "plan": plan}

# ===== recursive_search 子图节点 =====
def recursive_search_reference(state: PlannerState) -> PlannerState:
    """递归对未visited的entity进行搜索，调用伪爬虫（可升级为LLM工具）。"""
    plan = state.get("plan", {})
    if not plan:
        return state
        
    def crawl_unvisited(entity_node):
        if not entity_node.get('visited', False):
            # 这里可接入真实检索/爬虫/LLM工具
            results = pesudo_crawl(entity_node['entity'])
            entity_node['information'] = f"{entity_node['entity']} 的信息: {results}"
            entity_node['visited'] = True
        for child in entity_node.get('children', []):
            crawl_unvisited(child)
            
    # 复制plan对象以避免直接修改原对象
    import copy
    updated_plan = copy.deepcopy(plan)
    crawl_unvisited(updated_plan)
    
    return {**state, "plan": updated_plan}

def recursive_summarize_plan(state: PlannerState) -> PlannerState:
    """根据新搜索结果和当前plan递归更新plan json，调用LLM合并。"""
    import json
    from src.utils.llm import base_llm
    
    plan = state.get("plan", {})
    if not plan:
        return state
        
    # 将plan结构转为字符串，作为上下文
    plan_str = json.dumps(plan, ensure_ascii=False)
    messages = get_summarize_plan_messages(plan_str)
    llm = base_llm()
    response = llm.invoke(messages)
    try:
        updated_plan = json.loads(response.content)
    except Exception:
        import re
        match = re.search(r'\{[\s\S]*\}', response.content)
        updated_plan = json.loads(match.group()) if match else plan
    
    return {**state, "plan": updated_plan}

def check_all_visited(state: PlannerState) -> str:
    """判断plan树是否全部visited，决定是否继续递归。"""
    plan = state.get("plan", {})
    if not plan:
        return "return"
        
    def has_unvisited(entity_node):
        if not entity_node.get('visited', False):
            return True
        for child in entity_node.get('children', []):
            if has_unvisited(child):
                return True
        return False
        
    if has_unvisited(plan):
        return "recursive_search_reference"
    else:
        return "return"
