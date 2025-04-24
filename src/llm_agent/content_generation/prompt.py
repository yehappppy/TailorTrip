from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from typing import List

# 生成初始关键词的提示词
KEYWORD_GENERATION_PROMPT = """
根据用户的描述，生成一个初始搜索关键词，以帮助查找相关信息。
关键词应该简洁明了，但又要足够具体，能够产生有用的搜索结果。
请直接给出关键词，有且仅有一个关键词，不需要额外解释。
"""

# 从搜索结果提取关键词的提示词
KEYWORD_EXTRACTION_PROMPT = """
根据我刚刚提供的搜索结果，请识别出2-3个最重要的关键词或短语，这些词能够帮助我们进一步完善搜索。
这些关键词应该比原始搜索词更加具体，能够帮助我们找到具体的地点，而不是笼统的区域。

请只提取关键词，以英文逗号分隔。例如："京都赏樱地点, 円山公园开放时间, 艺伎表演最佳时段"
"""

# 评估搜索结果是否包含特定地点信息的提示词
RESULT_EVALUATION_PROMPT = """
请评估搜索结果是否包含关于特定的、可行动的、可以访问的地点信息。

特定地点是指类似"位于123号大街的XYZ餐厅"或"ABC公园，樱花观赏时间为上午9点至下午5点"这样的信息。
非特定地点是指类似"市中心区域"或"东京的餐厅"这样没有具体名称或地址的笼统描述。

根据这个标准，搜索结果是否包含特定地点信息？
只需回答"Yes"或"No"。
"""

# 生成最终回答的提示词
FINAL_RESPONSE_PROMPT = """
请根据以下搜索树的信息和用户的原始输入，生成一个全面且连贯的回答。
回答应该：
1. 综合搜索到的信息与用户的偏好进行决策
2. 保持逻辑性和连贯性
3. 突出最相关和最重要的信息，忽略较无关的信息。
4. 使用适当的分类和结构
5. 确保信息的准确性
"""

# 示例输入和输出
KEYWORD_GENERATION_SAMPLE_INPUT = "我想去一个有美丽海滩和美食的地方度假，预算适中，最好有一些文化体验"
KEYWORD_GENERATION_SAMPLE_OUTPUT = "东南亚海岛度假目的地"

KEYWORD_EXTRACTION_SAMPLE_INPUT = "泰国普吉岛是东南亚最受欢迎的海岛度假胜地之一，以其白色沙滩、清澈海水和丰富的水上活动而闻名。岛上有多个海滩区域，如芭东海滩、卡塔海滩和卡伦海滩等。普吉岛的美食也非常有名，尤其是泰式海鲜料理。游客可以参观大佛、查龙寺等文化景点，也可以体验泰式按摩和夜市购物。住宿选择从经济型旅馆到豪华度假村应有尽有，交通可以选择出租车、嘟嘟车或租摩托车。"
KEYWORD_EXTRACTION_SAMPLE_OUTPUT = "芭东海滩景点, 普吉岛泰式海鲜餐厅, 查龙寺开放时间"

RESULT_EVALUATION_SAMPLE_INPUT = "芭东海滩位于普吉岛西海岸，是岛上最热闹的海滩，长约3公里。这里有细腻的白沙和清澈的海水，是游泳、日光浴和水上运动的理想场所。海滩沿线有众多餐厅、酒吧和购物中心，如江西冷购物中心。最佳游览时间是11月至4月的旱季。可以从普吉镇乘坐公共巴士或出租车前往，车程约30分钟。海滩上有遮阳伞和躺椅出租，价格约为200泰铢/天。"
RESULT_EVALUATION_SAMPLE_OUTPUT = "Yes"


def get_chatbot_prompt(context: str, question: str) -> str:
    return CHATBOT_PROMPT.format(context=context, question=question)


def get_keyword_generation_messages(user_description: str) -> List:
    """获取生成初始关键词的消息列表"""
    return [
        SystemMessage(content=KEYWORD_GENERATION_PROMPT),
        HumanMessage(content=KEYWORD_GENERATION_SAMPLE_INPUT),
        AIMessage(content=KEYWORD_GENERATION_SAMPLE_OUTPUT),
        HumanMessage(content=f"用户描述: {user_description}")
    ]


def get_keyword_extraction_messages(search_result: str) -> List:
    """获取从搜索结果中提取关键词的消息列表"""
    return [
        SystemMessage(content=KEYWORD_EXTRACTION_PROMPT),
        HumanMessage(content=KEYWORD_EXTRACTION_SAMPLE_INPUT),
        AIMessage(content=KEYWORD_EXTRACTION_SAMPLE_OUTPUT),
        HumanMessage(content=f"搜索结果: {search_result}")
    ]


def get_result_evaluation_messages(search_result: str) -> List:
    """获取评估搜索结果是否包含特定地点信息的消息列表"""
    return [
        SystemMessage(content=RESULT_EVALUATION_PROMPT),
        HumanMessage(content=RESULT_EVALUATION_SAMPLE_INPUT),
        AIMessage(content=RESULT_EVALUATION_SAMPLE_OUTPUT),
        HumanMessage(content=f"搜索结果: {search_result}")
    ]


def get_final_response_messages(user_input: str, tree_json: str) -> List:
    """获取生成最终回答的消息列表"""
    prompt = f"""
    用户原始输入：
    {user_input}
    
    搜索树信息：
    {tree_json}
    
    请生成最终回答：
    """
    return [SystemMessage(content=FINAL_RESPONSE_PROMPT), HumanMessage(content=prompt)]