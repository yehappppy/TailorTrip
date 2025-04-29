from typing import Dict, Any, List
import json
import copy
from src.utils.llm import base_llm
from src.utils.util import get_logger
from src.llm_agent.new_planner.planning import get_plan_generation_messages, parse_plan_json

logger = get_logger("new_planner.recursive")

# 导入 src.tools.crawl 中的 pesudo_crawl 函数
from src.tools.crawl import pesudo_crawl

def search_entity(entity: str) -> List[str]:
    """
    搜索实体相关的参考信息
    
    Args:
        entity: 实体名称
        
    Returns:
        List[str]: 搜索结果列表
    """
    # 使用 pesudo_crawl 函数获取搜索结果
    # 使用 invoke 方法代替 __call__
    try:
        return pesudo_crawl.invoke(entity)
    except AttributeError:
        # 兼容旧版本
        print("  [警告] pesudo_crawl 使用了已弃用的 __call__ 方法，将在未来版本中移除")
        return pesudo_crawl(entity)

def update_entity_information(entity_node: Dict[str, Any]) -> Dict[str, Any]:
    """
    更新实体节点的信息
    
    Args:
        entity_node: 实体节点字典
        
    Returns:
        Dict[str, Any]: 更新后的实体节点
    """
    # 创建新的节点对象，避免直接修改原对象
    new_node = copy.deepcopy(entity_node)
    entity_name = new_node.get('entity', '')
    
    # 如果实体信息还不完善，则进行搜索
    if not new_node.get('well_known', False):
        if entity_name:
            print(f"  [搜索实体] 搜索实体: {entity_name}")
            
            # 搜索实体信息
            results = search_entity(entity_name)
            # 将搜索结果合并为一个字符串
            info_text = "\n".join(results) if isinstance(results, list) else str(results)
            new_node['information'] = info_text
            
            print(f"  [搜索结果] 实体: {entity_name}, 结果长度: {len(info_text)} 字符")
            
            # 判断信息是否包含可实践性内容（如地点、价格、时间等）
            # 这里简单判断信息长度，实际项目中可使用更复杂的逻辑
            has_practical_info = len(info_text) > 100 and (
                '价格' in info_text or 
                '地址' in info_text or 
                '时间' in info_text or 
                '门票' in info_text
            )
            
            if has_practical_info:
                new_node['well_known'] = True
                print(f"  [实体评估] 实体 '{entity_name}' 已包含可实践性内容")
                logger.info(f"实体 '{entity_name}' 的信息已包含可实践性内容")
            else:
                new_node['well_known'] = False
                print(f"  [实体评估] 实体 '{entity_name}' 不包含足够的可实践性内容")
                logger.info(f"实体 '{entity_name}' 的信息不包含足够的可实践性内容")
    else:
        print(f"  [跳过搜索] 实体 '{entity_name}' 已经包含足够信息")
    
    # 递归处理子节点
    print(f"  [处理子节点] 实体 '{entity_name}' 有 {len(new_node.get('children', []))} 个子节点")
    new_children = []
    for child in new_node.get('children', []):
        new_child = update_entity_information(child)
        new_children.append(new_child)
    
    # 更新子节点列表
    new_node['children'] = new_children
    
    return new_node

def has_unknown_entities(plan: Dict[str, Any]) -> bool:
    """
    检查计划中是否有信息不完善的实体
    
    Args:
        plan: 规划字典
        
    Returns:
        bool: 如果有信息不完善的实体则返回True，否则返回False
    """
    def check_node(node):
        # 如果该实体信息不完善（well_known 为 False）
        if not node.get('well_known', False):
            return True
        # 递归检查子节点
        for child in node.get('children', []):
            if check_node(child):
                return True
        return False
    
    return check_node(plan)

def update_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    使用LLM更新规划
    
    Args:
        plan: 当前规划字典
        
    Returns:
        Dict[str, Any]: 更新后的规划字典
    """
    print("\n" + "-"*50)
    print("[更新规划] 开始更新规划JSON")
    
    # 将计划结构转为字符串，作为上下文
    plan_str = json.dumps(plan, ensure_ascii=False)
    messages = get_plan_generation_messages(plan_str)
    llm = base_llm()
    response = llm.invoke(messages)
    
    # 解析更新后的规划
    updated_plan = parse_plan_json(response.content)
    
    # 打印更新后的规划
    if updated_plan:
        print("[更新规划JSON] 更新成功")
        print(json.dumps(updated_plan, ensure_ascii=False, indent=2))
    else:
        print("[更新规划JSON] 解析失败，使用原计划")
    
    print("-"*50)
    
    # 如果解析失败，返回原计划
    return updated_plan if updated_plan else plan

def recursive_search(initial_result: Dict[str, Any], max_depth: int = 3) -> Dict[str, Any]:
    """
    执行递归搜索和规划更新
    
    Args:
        initial_result: 初始规划结果，包含plan和references
        max_depth: 最大递归深度
        
    Returns:
        Dict[str, Any]: 最终规划结果
    """
    print("\n" + "-"*50)
    print("[递归搜索] 开始递归搜索和规划更新")
    
    # 获取初始规划和参考信息
    plan = initial_result.get('plan', {})
    references = initial_result.get('references', [])
    
    if not plan:
        logger.warning("初始规划为空，无法执行递归搜索")
        print("[递归搜索] 错误: 初始规划为空")
        print("-"*50)
        return initial_result
    
    # 复制计划对象以避免直接修改原对象
    current_plan = copy.deepcopy(plan)
    all_references = list(references)  # 保存所有参考信息
    current_depth = 0
    
    # 递归搜索和更新，直到所有实体都包含足够信息或达到最大深度
    while has_unknown_entities(current_plan) and current_depth < max_depth:
        print("\n" + "-"*50)
        print(f"[递归搜索] 执行第 {current_depth + 1} 轮递归搜索")
        logger.info(f"执行第 {current_depth + 1} 轮递归搜索")
        
        # 更新实体信息
        print("[更新实体信息] 开始更新实体信息")
        current_plan = update_entity_information(current_plan)
        print("[更新实体信息] 更新完成")
        
        # 收集新的参考信息
        def collect_references(node):
            if node.get('information'):
                all_references.append(node.get('information'))
            for child in node.get('children', []):
                collect_references(child)
        
        collect_references(current_plan)
        print(f"[参考信息] 当前收集到的参考信息数量: {len(all_references)}")
        
        # 使用LLM更新规划
        current_plan = update_plan(current_plan)
        
        current_depth += 1
        print("-"*50)
    
    logger.info(f"递归搜索完成，共执行 {current_depth} 轮")
    print(f"[递归搜索] 完成，共执行 {current_depth} 轮")
    print("-"*50)
    
    # 返回最终结果
    return {
        "references": all_references,
        "plan": current_plan
    }
