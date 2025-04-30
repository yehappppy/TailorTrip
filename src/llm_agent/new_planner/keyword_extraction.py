from typing import List
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from src.utils.llm import fast_llm

# 关键词提取提示词
KEYWORD_EXTRACTION_PROMPT = """
请根据用户输入，提取一个最相关且唯一的关键词。
只需返回关键词本身，不要额外解释。
"""

# 示例输入输出
KEYWORD_EXTRACTION_SAMPLE_INPUT = "我想了解巴黎的著名景点和历史。"
KEYWORD_EXTRACTION_SAMPLE_OUTPUT = "巴黎景点"

def get_keyword_extraction_messages(user_input: str) -> List:
    """
    构建关键词提取的消息列表
    
    Args:
        user_input: 用户输入的查询或需求描述
        
    Returns:
        List: 包含系统提示、示例和用户输入的消息列表
    """
    return [
        SystemMessage(content=KEYWORD_EXTRACTION_PROMPT),
        HumanMessage(content=KEYWORD_EXTRACTION_SAMPLE_INPUT),
        AIMessage(content=KEYWORD_EXTRACTION_SAMPLE_OUTPUT),
        HumanMessage(content=f"用户输入: {user_input}")
    ]

def extract_keyword(user_input: str) -> str:
    """
    从用户输入中提取关键词
    
    Args:
        user_input: 用户输入的查询或需求描述
        
    Returns:
        str: 提取的关键词
    """
    messages = get_keyword_extraction_messages(user_input)
    llm = fast_llm()
    response = llm.invoke(messages)
    
    # 清理LLM响应，提取纯关键词
    keyword = response.content.strip()
    keyword = keyword.replace('关键词：', '').replace('关键词:', '')
    keyword = keyword.replace('"', '').replace('"','').replace('"','')
    
    return keyword


# 实体提取提示词
EXTRACTION_PROMPT = """
你将充当关键词提取助手，请根据用户提供的搜索结果，为主关键词提取子实体关键词。

*实体提取要求：*
- 只提取比当前关键词在概念范围上更小的实体。
  - 例如，从"滇池"的参考资料中不应该提取出"昆明"或"云南"。
  - 提取出的实体不能和当前关键词一样。
- 只提取子一级的实体，不直接提取最细节的实体。
  - 例如，从"云南"的参考资料中应该提取出"昆明,大理"
  - 例如，从"云南"的参考资料中不应该提取出"崇圣寺三塔,普达措国家公园"
- 如果子实体容易被混淆，则需要加上父实体作为前缀。
  - 例如：在父实体"昆明"下，"酒吧街"应该改为"昆明酒吧街"；在父实体"滇池"下，"红嘴鸥"应改为"滇池红嘴鸥"
- 不提取过于笼统宽泛的词汇。
  - 例如"春天"、"美食"、"风景"等。
- 提取的实体应该是具体的地点、景点、建筑或游玩项目等。
- 最多提取出5个最相关的子实体，如果关键词已经是较为细节的实体，直接返回空字符串。
- 每次提取的结果之间相互独立。

只需返回逗号分隔的实体列表，不要额外解释。
"""
EXTRACTION_SAMPLE_INPUT1 = "云南旅游景点众多，包括昆明的滇池、石林，大理的洱海、苍山，丽江的玉龙雪山、古城，香格里拉的普达措国家公园等。其中丽江古城是世界文化遗产，洱海是云南第二大淡水湖。"
EXTRACTION_SAMPLE_OUTPUT1 = "昆明,大理,丽江"
EXTRACTION_SAMPLE_INPUT2 = "昆明，云南省会，素有春城美誉，年均气温15℃左右，四季花开不败。这座高原城市坐拥滇池碧波、石林奇观和西山森林公园等自然胜景，民族村集中展示25个少数民族文化风情。作为亚洲地理中心，昆明融合汉、彝、白、傣等多民族文化，街头巷尾飘荡着过桥米线、汽锅鸡的香气，斗南花卉市场每日流转百万支鲜花。宜人气候与慢节奏生活，使其成为理想的康养旅居目的地，更是通往大理、丽江、西双版纳等热门景区的交通枢纽。"
EXTRACTION_SAMPLE_OUTPUT2 = "滇池,云南石林奇观,昆明西山森林公园,斗南花卉市场"

def get_extraction_messages(search_result: str) -> List:
    """获取实体提取的消息列表"""
    return [
        SystemMessage(content=EXTRACTION_PROMPT),
        HumanMessage(content=EXTRACTION_SAMPLE_INPUT1),
        AIMessage(content=EXTRACTION_SAMPLE_OUTPUT1),
        HumanMessage(content=EXTRACTION_SAMPLE_INPUT2),
        AIMessage(content=EXTRACTION_SAMPLE_OUTPUT2),
        HumanMessage(content=search_result)
    ]

def extract_entities(search_result: str) -> List[str]:
    """
    从搜索结果中提取实体关键词
    
    Args:
        search_result: 搜索结果文本
        
    Returns:
        List[str]: 提取的实体关键词列表
    """
    messages = get_extraction_messages(search_result)
    llm = fast_llm()
    response = llm.invoke(messages)
    
    # 解析响应内容，预期是逗号分隔的实体列表
    entities_text = response.content.strip()
    if not entities_text:
        return []
    
    # 分割并清理实体列表
    entities = [e.strip() for e in entities_text.split(',') if e.strip()]
    return entities
