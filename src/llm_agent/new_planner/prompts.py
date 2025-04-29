from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from typing import List

# 生成初始关键词的提示词
KEYWORD_GENERATION_PROMPT = """
请根据用户输入，提取一个最相关且唯一的关键词。
只需返回关键词本身，不要额外解释。
"""
KEYWORD_GENERATION_SAMPLE_INPUT = "我想了解巴黎的著名景点和历史。"
KEYWORD_GENERATION_SAMPLE_OUTPUT = "巴黎景点"

def get_keyword_generation_messages(user_input: str) -> List:
    """获取生成初始关键词的消息列表"""
    return [
        SystemMessage(content=KEYWORD_GENERATION_PROMPT),
        HumanMessage(content=KEYWORD_GENERATION_SAMPLE_INPUT),
        AIMessage(content=KEYWORD_GENERATION_SAMPLE_OUTPUT),
        HumanMessage(content=f"用户输入: {user_input}")
    ]

# 总结规划提示词
SUMMARIZE_PLAN_PROMPT = """
请根据以下搜索结果，将其总结为分层的多选框JSON，包含如下字段：
- entity（实体名称）
- information（从爬取结果中总结与该entity相关的信息）
- children（子元素列表，子元素和父元素格式一致）
- visited（关于entity的信息是否被充分了解了，true/false）
"""
SUMMARIZE_PLAN_SAMPLE_INPUT = "巴黎景点包括埃菲尔铁塔、卢浮宫、凯旋门等，这些都是世界著名的旅游胜地。\n埃菲尔铁塔是巴黎最著名的旅游景点之一，建于1889年，高324米，是当时世界上最高的建筑物。"
SUMMARIZE_PLAN_SAMPLE_OUTPUT = """
{
  "entity": "巴黎景点",
  "information": "巴黎景点包括埃菲尔铁塔、卢浮宫、凯旋门等，这些都是世界著名的旅游胜地。",
  "visited": true,
  "children": [
    {
      "entity": "埃菲尔铁塔",
      "information": "埃菲尔铁塔是巴黎最著名的旅游景点之一，建于1889年，高324米，是当时世界上最高的建筑物。",
      "visited": true,
      "children": []
    },
    {
      "entity": "卢浮宫",
      "information": "",
      "visited": false,
      "children": []
    },
    {
      "entity": "凯旋门",
      "information": "",
      "visited": false,
      "children": []
    }
  ]
}
"""

def get_summarize_plan_messages(search_result: str) -> List:
    """获取总结规划的消息列表"""
    return [
        SystemMessage(content=SUMMARIZE_PLAN_PROMPT),
        HumanMessage(content=SUMMARIZE_PLAN_SAMPLE_INPUT),
        AIMessage(content=SUMMARIZE_PLAN_SAMPLE_OUTPUT),
        HumanMessage(content=search_result)
    ]

# 规划生成提示模板
PLAN_GENERATION_PROMPT = """
请根据以下搜索结果，将其总结为分层的多选框JSON，包含如下字段：
- entity（实体名称）
- information（从爬取结果中总结与该entity相关的信息）
- children（子元素列表，子元素和父元素格式一致）
- well_known（该entity的信息是否包含了大部分可实践性信息，如具体的地点位置、价格、时间等，true/false）

注意：如果information包含了大部分关于该entity的可实践性信息（如具体的地点位置、价格、时间等等），则well_known为true，反之则为false。在children中应添加搜索后有可能让well_known变为true的entity。
"""

# 示例输入输出
PLAN_GENERATION_SAMPLE_INPUT = "巴黎景点包括埃菲尔铁塔、卢浮宫、凯旋门等，这些都是世界著名的旅游胜地。\n埃菲尔铁塔是巴黎最著名的旅游景点之一，建于1889年，高324米，是当时世界上最高的建筑物。"
PLAN_GENERATION_SAMPLE_OUTPUT = """
{
  "entity": "巴黎景点",
  "information": "巴黎景点包括埃菲尔铁塔、卢浮宫、凯旋门等，这些都是世界著名的旅游胜地。",
  "well_known": true,
  "children": [
    {
      "entity": "埃菲尔铁塔",
      "information": "埃菲尔铁塔是巴黎最著名的旅游景点之一，建于1889年，高324米，是当时世界上最高的建筑物。开放时间：每天9:00-23:00，门票：成人16欧元，地址：Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France。",
      "well_known": true,
      "children": []
    },
    {
      "entity": "卢浮宫",
      "information": "",
      "well_known": false,
      "children": []
    },
    {
      "entity": "凯旋门",
      "information": "",
      "well_known": false,
      "children": []
    }
  ]
}
"""

def get_plan_generation_messages(search_result: str) -> List:
    """
    构建规划生成的消息列表
    
    Args:
        search_result: 搜索结果文本
        
    Returns:
        List: 包含系统提示、示例和搜索结果的消息列表
    """
    return [
        SystemMessage(content=PLAN_GENERATION_PROMPT),
        HumanMessage(content=PLAN_GENERATION_SAMPLE_INPUT),
        AIMessage(content=PLAN_GENERATION_SAMPLE_OUTPUT),
        HumanMessage(content=search_result)
    ]
