from typing import Dict, Any, List
import json
import copy
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from src.utils.llm import base_llm, fast_llm
from src.utils.util import get_logger, structure_output
from src.llm_agent.content_generation.planning import search_entity_info, update_plan_with_info, create_initial_plan
from src.llm_agent.content_generation.keyword_extraction import extract_entities

logger = get_logger("content_generation.recursive")

def check_entity_exists(entity: str, plan_tree: Dict[str, Any]) -> bool:
    """
    检查实体是否已存在于规划树中
    
    Args:
        entity: 要检查的实体名称
        plan_tree: 规划树
        
    Returns:
        bool: 如果实体已存在则返回True，否则返回False
    """
    # 如果实体为空或规划树为空，直接返回False
    if not entity or not plan_tree:
        return False
        
    # 检查当前节点
    current_entity = plan_tree.get('entity', '')
    if current_entity:
        # 完全匹配
        if current_entity.lower() == entity.lower():
            logger.info(f"实体 '{entity}' 与当前节点 '{current_entity}' 完全匹配")
            return True
        
        # 更精确的包含关系检查
        # 1. 检查实体是否是当前节点的子字符串
        if entity.lower() in current_entity.lower() and len(entity) > 3:
            # 只有当实体长度足够时，才考虑子字符串关系
            logger.info(f"实体 '{entity}' 是当前节点 '{current_entity}' 的子字符串")
            return True
            
        # 2. 检查当前节点是否是实体的子字符串
        if current_entity.lower() in entity.lower() and len(current_entity) > 3:
            # 只有当当前节点长度足够时，才考虑子字符串关系
            logger.info(f"当前节点 '{current_entity}' 是实体 '{entity}' 的子字符串")
            return True
    
    # 递归检查子节点
    for child in plan_tree.get('children', []):
        if check_entity_exists(entity, child):
            return True
    
    return False

def extract_child_entities(information: str, parent_entity: str = "", plan_tree: Dict[str, Any] = None) -> List[str]:
    """
    从信息中提取子实体关键词，最多提取出5个
    
    Args:
        information: 实体信息文本
        parent_entity: 父实体名称，用于日志记录
        plan_tree: 完整的规划树，用于检查实体是否重复
        
    Returns:
        List[str]: 子实体关键词列表，最多5个
    """
    if not information or len(information.strip()) < 50:  # 增加了最小信息长度要求
        logger.info(f"实体 '{parent_entity}' 的信息过短，不提取子实体")
        return []
    
    # 使用extract_entities函数提取子实体
    entities = extract_entities(information)
    
    # 如果实体列表为空，将作为叶节点返回
    if not entities:
        logger.info(f"实体 '{parent_entity}' 未提取到子实体，将作为叶节点返回")
        print(f"  [子实体提取] 实体 '{parent_entity}' 未提取到子实体，将作为叶节点")
        return []
    
    # 如果提供了规划树，过滤掉已存在的实体
    if plan_tree is not None:
        original_entities = entities.copy()
        filtered_entities = []
        
        # 过滤已存在的实体
        for entity in original_entities:
            if check_entity_exists(entity, plan_tree):
                filtered_entities.append(entity)
                print(f"  [实体过滤] 实体 '{entity}' 已存在于规划树中，已过滤")
            else:
                print(f"  [实体保留] 实体 '{entity}' 不存在于规划树中，已保留")
        
        # 更新实体列表
        entities = [e for e in original_entities if e not in filtered_entities]
        
        # 记录被过滤掉的实体
        if filtered_entities:
            logger.info(f"实体 '{parent_entity}' 过滤掉已存在的实体: {', '.join(filtered_entities)}")
            print(f"  [实体过滤统计] 共过滤掉 {len(filtered_entities)} 个实体，保留 {len(entities)} 个实体")
    
    # 限制最多5个实体
    if len(entities) > 5:
        logger.info(f"实体 '{parent_entity}' 提取到 {len(entities)} 个子实体，只保留前5个")
        entities = entities[:5]
    else:
        logger.info(f"实体 '{parent_entity}' 提取到 {len(entities)} 个子实体")
    
    return entities

def get_information_completeness_messages(entity: str) -> List:
    """
    构建信息完整性判断的消息列表
    
    Args:
        entity: 实体名称
        
    Returns:
        List: 包含系统提示和实体信息的消息列表
    """
    # 信息完整性判断提示词
    INFORMATION_COMPLETENESS_PROMPT = """
    你将作为旅游规划助手，负责判断一个旅游实体是否为底层具体实体，不需要进一步细化。

    判断标准：只有极其具体的实体才能被称为完整，不需要进一步细化。判断它在对应的实体类型中是否为底层实体：

    1. 景点类：是否为一个具体的景区或景点，而不是一个地区或城市
       - 完整实体例子："西湖断桥"、"滇池海埕公园"、"大理崖城"
       - 需要细化的实体例子："杭州"、"云南"、"西湖"、"滇池"

    2. 美食类：是否为一家具体的餐厅或小吃店，而不是一类食物
       - 完整实体例子："杭州知味观"、"昆明文林街小吃"
       - 需要细化的实体例子："杭州菜"、"过桥米线"、"昆明小吃"

    3. 活动类：是否为一个具体的活动或项目，而不是一类活动
       - 完整实体例子："丽江古城酒吧街夜游"、"西湖游船"
       - 需要细化的实体例子："西湖游玩"、"丽江夜生活"

    4. 住宿类：是否为一家具体的酒店或客栈，而不是一类住宿
       - 完整实体例子："杭州西子湖四季酒店"、"丽江古城客栈"
       - 需要细化的实体例子："杭州酒店"、"丽江客栈"

    请根据以上标准，判断提供的实体是否为底层具体实体，不需要进一步细化。
    只需回答"true"或"false"，不需要解释。
    """

    # 样例1：底层具体实体，返回true
    INFORMATION_COMPLETENESS_SAMPLE_INPUT1 = "杭州西湖断桥"
    INFORMATION_COMPLETENESS_SAMPLE_OUTPUT1 = "true"

    # 样例2：非底层实体，需要细化，返回false
    INFORMATION_COMPLETENESS_SAMPLE_INPUT2 = "云南旅游"
    INFORMATION_COMPLETENESS_SAMPLE_OUTPUT2 = "false"
    
    return [
        SystemMessage(content=INFORMATION_COMPLETENESS_PROMPT),
        HumanMessage(content=INFORMATION_COMPLETENESS_SAMPLE_INPUT1),
        AIMessage(content=INFORMATION_COMPLETENESS_SAMPLE_OUTPUT1),
        HumanMessage(content=INFORMATION_COMPLETENESS_SAMPLE_INPUT2),
        AIMessage(content=INFORMATION_COMPLETENESS_SAMPLE_OUTPUT2),
        HumanMessage(content=entity),
    ]

def is_information_complete(information: str, entity_name: str = "") -> bool:
    """
    使用LLM判断实体是否为底层具体实体，不需要进一步细化
    
    Args:
        information: 实体信息文本（现在不再使用，但保留参数以保持兼容性）
        entity_name: 实体名称
        
    Returns:
        bool: 如果实体为底层具体实体返回True，否则返回False
    """
    # 如果信息为空或过短，则认为需要细化
    if not entity_name:
        return False
    
    # 使用LLM判断实体是否为底层具体实体
    messages = get_information_completeness_messages(entity_name)
    llm = fast_llm()
    response = llm.invoke(messages)
    
    # 解析响应内容，预期是"true"或"false"
    result = response.content.strip().lower()
    is_complete = (result == "true")
    
    logger.info(f"实体 '{entity_name}' 信息完整性判断结果: {is_complete}")
    print(f"  [完整性判断] 实体 '{entity_name}' 是否为底层具体实体: {is_complete}")
    
    return is_complete

def get_node_depth(node: Dict[str, Any]) -> int:
    """
    计算节点的深度（从当前节点到最深叶子节点的距离）
    
    Args:
        node: 当前节点
        
    Returns:
        int: 节点深度，叶子节点深度为0
    """
    if not node.get('children', []):
        return 0
    
    max_child_depth = 0
    for child in node.get('children', []):
        child_depth = get_node_depth(child)
        max_child_depth = max(max_child_depth, child_depth)
    
    return max_child_depth + 1


def update_node_with_info(node: Dict[str, Any], root_node: Dict[str, Any] = None, max_depth: int = 3, current_level: int = 0, parent_entity: str = "根节点") -> Dict[str, Any]:
    """
    递归更新节点信息
    
    Args:
        node: 当前节点
        root_node: 规划树的根节点，用于全局实体检查
        max_depth: 最大深度限制，同时控制递归深度和树高度
        current_level: 当前节点在树中的层级，根节点为0
        parent_entity: 父节点的实体名称
        
    Returns:
        Dict[str, Any]: 更新后的节点
    """
    # 如果没有提供根节点，则使用当前节点作为根节点
    if root_node is None:
        root_node = node
    # 创建新的节点对象，避免直接修改原对象
    new_node = copy.deepcopy(node)
    entity_name = new_node.get('entity', '')
    
    # 计算当前节点在树中的层级（从根节点到当前节点的距离）
    # 这里我们通过计算根节点的深度来近似判断
    current_tree_height = get_node_depth(root_node) + 1
    
    # 如果节点信息不完整，则进行搜索和更新
    if not new_node.get('is_complete', False) and entity_name:
        print(f"  [层级{current_level}|父:{parent_entity}] [搜索实体] {entity_name}")
        
        # 搜索实体信息
        search_results = search_entity_info(entity_name)
        
        # 将搜索结果合并为一个字符串
        info_text = "\n".join(search_results) if isinstance(search_results, list) else str(search_results)
        
        # 更新节点信息
        new_node['information'] = info_text
        
        # 判断信息是否需要继续细化
        needs_children = not is_information_complete(info_text, entity_name)
        
        # 如果当前层级已经达到最大限制，则不再添加子节点
        if current_level >= max_depth - 1:  # 减1是因为子节点将在下一层
            needs_children = False
            print(f"  [层级{current_level}|父:{parent_entity}] [高度限制] {entity_name}: 已达到最大深度 {max_depth}，不再添加子节点")
        
        print(f"  [层级{current_level}|父:{parent_entity}] [信息评估] {entity_name}: {'需要细化' if needs_children else '不需要细化'}, 长度: {len(info_text)} 字符")
        
        # 无论是否需要细化，都将节点标记为完成，因为它已经被搜索过了
        new_node['is_complete'] = True
        
        # 如果信息需要继续细化，则提取子实体
        if needs_children:
            # 如果没有提供根节点，则使用当前节点作为根节点
            tree_root = root_node if root_node is not None else new_node
            child_entities = extract_child_entities(info_text, entity_name, tree_root)
            
            # 如果提取到的子实体为空，则直接设置空子节点列表
            if not child_entities:
                print(f"  [层级{current_level}|父:{parent_entity}] [节点标记] {entity_name} 没有子实体，已标记为完整节点（叶节点）")
                new_node['children'] = []
            else:
                print(f"  [层级{current_level}|父:{parent_entity}] [子实体提取] {entity_name} -> {', '.join(child_entities)}")
                    
                # 为每个子实体创建节点
                children = []
                for child_entity in child_entities:
                    child_node = {
                        "entity": child_entity,
                        "information": "",
                        "is_complete": False,
                        "children": []
                    }
                    children.append(child_node)
                
                # 设置子节点
                new_node['children'] = children
                print(f"  [层级{current_level}|父:{parent_entity}] [节点标记] {entity_name} 添加了 {len(children)} 个子节点")
        else:
            # 如果信息不需要细化，则设置空子节点列表
            print(f"  [层级{current_level}|父:{parent_entity}] [节点标记] {entity_name} 信息已充分，已标记为完整节点")
            new_node['children'] = []
    else:
        print(f"  [层级{current_level}|父:{parent_entity}] [跳过搜索] {entity_name}: {'已完整' if new_node.get('is_complete', False) else '无实体名'}")
    
    # 递归处理子节点 - 无论节点是否完整，都递归处理子节点
    new_children = []
    for child in new_node.get('children', []):
        # 始终使用最初传入的根节点，确保在整个规划树中检查实体
        # 子节点层级加1，父实体为当前节点的实体名
        updated_child = update_node_with_info(child, root_node, max_depth, current_level + 1, entity_name)
        new_children.append(updated_child)
    
    # 更新子节点列表
    new_node['children'] = new_children
    
    return new_node

def has_incomplete_nodes(plan: Dict[str, Any]) -> bool:
    """
    检查规划中是否有需要继续处理的节点
    
    Args:
        plan: 规划字典
        
    Returns:
        bool: 如果有需要继续处理的节点则返回True，否则返回False
    """
    if not plan:
        return False
        
    def check_node(node):
        # 如果节点没有标记为完成，则需要继续处理
        if not node.get('is_complete', False):
            return True
            
        # 递归检查子节点
        for child in node.get('children', []):
            if check_node(child):
                return True
                
        return False
    
    return check_node(plan)

def collect_all_references(node: Dict[str, Any], references: List[str]):
    """
    递归收集所有参考信息
    
    Args:
        node: 当前节点
        references: 参考信息列表，将被修改
    """
    if node.get('information'):
        info = node.get('information')
        if info and len(info.strip()) > 10:
            references.append(info)
    
    for child in node.get('children', []):
        collect_all_references(child, references)

def recursive_search(initial_result: Dict[str, Any], max_depth: int = 2) -> Dict[str, Any]:
    """
    执行递归规划
    
    Args:
        initial_result: 初始结果，包含references和plan
        max_depth: 最大深度限制，同时控制递归轮数和树高度
        
    Returns:
        Dict[str, Any]: 最终规划结果
    """
    print("\n" + "-"*50)
    print("[递归规划] 开始递归规划过程")
    
    # 获取初始参考信息
    references = initial_result.get('references', [])
    keyword = ""
    
    # 获取初始规划，如果为空则创建一个
    plan = initial_result.get('plan', {})
    if not plan and references:
        # 从参考信息中提取关键词
        info_text = "\n".join(references) if isinstance(references, list) else str(references)
        entities = extract_child_entities(info_text)
        if entities:
            keyword = entities[0]
        else:
            # 如果无法提取关键词，使用默认值
            keyword = "旅游规划"
            
        # 创建初始规划
        plan = create_initial_plan(keyword)
        print(f"[初始规划] 为关键词 '{keyword}' 创建初始规划节点")
    
    if not plan:
        logger.warning("无法创建初始规划，递归规划终止")
        print("[递归规划] 错误: 无法创建初始规划")
        print("-"*50)
        return initial_result
    
    # 复制计划对象以避免直接修改原对象
    current_plan = copy.deepcopy(plan)
    all_references = list(references)  # 保存所有参考信息
    current_depth = 0
    
    # 递归规划循环，直到所有节点都包含完整信息或达到最大深度
    while has_incomplete_nodes(current_plan) and current_depth < max_depth:
        print("\n" + "-"*50)
        print(f"[递归规划] 执行第 {current_depth + 1} 轮递归规划")
        logger.info(f"执行第 {current_depth + 1} 轮递归规划")
        
        # 更新节点信息
        print("[更新节点] 开始更新节点信息")
        # 将当前计划作为根节点传递，用于检查实体是否重复
        # 在每轮递归开始时，我们都使用当前的完整规划树作为根节点
        print(f"[实体检查] 开始检查实体是否重复，使用完整规划树")
        # 根节点层级为0，父实体为"根节点"
        current_plan = update_node_with_info(current_plan, current_plan, max_depth, 0, "根节点")
        print("[更新节点] 更新完成")
        
        # 收集新的参考信息
        all_references = []
        collect_all_references(current_plan, all_references)
        print(f"[参考信息] 当前收集到的参考信息数量: {len(all_references)}")
        
        current_depth += 1
        print("-"*50)
    
    logger.info(f"递归规划完成，共执行 {current_depth} 轮")
    print(f"[递归规划] 完成，共执行 {current_depth} 轮")
    print("-"*50)
    
    # 返回最终结果
    return {
        "references": all_references,
        "plan": current_plan
    }
