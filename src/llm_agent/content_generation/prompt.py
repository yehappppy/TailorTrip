from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from typing import List

# 生成初始关键词的提示词
KEYWORD_GENERATION_PROMPT = """
根据用户的描述，生成一个初始搜索关键词，以帮助查找相关信息。
关键词应该简洁明了，但又要足够具体，能够产生有用的搜索结果。
请直接给出关键词，有且仅有一个关键词，不需要额外解释。
"""

# 示例输入和输出
KEYWORD_GENERATION_SAMPLE_INPUT = "我想去一个有美丽海滩和美食的地方度假，预算适中，最好有一些文化体验"
KEYWORD_GENERATION_SAMPLE_OUTPUT = "东南亚海岛度假目的地"

def get_keyword_generation_messages(user_description: str) -> List:
    """获取生成初始关键词的消息列表"""
    return [
        SystemMessage(content=KEYWORD_GENERATION_PROMPT),
        HumanMessage(content=KEYWORD_GENERATION_SAMPLE_INPUT),
        AIMessage(content=KEYWORD_GENERATION_SAMPLE_OUTPUT),
        HumanMessage(content=f"用户描述: {user_description}")
    ]


# 从搜索结果提取关键词的提示词
KEYWORD_EXTRACTION_PROMPT = """
根据我刚刚提供的搜索结果，请识别出2-3个最重要的关键词或短语，这些词能够帮助我们进一步完善搜索。
这些关键词应该比原始搜索词更加具体，能够帮助我们找到具体的地点，而不是笼统的区域。

请只提取关键词，以英文逗号分隔。例如："京都赏樱地点, 円山公园开放时间, 艺伎表演最佳时段"
"""

# 示例输入和输出
KEYWORD_EXTRACTION_SAMPLE_INPUT = "泰国普吉岛是东南亚最受欢迎的海岛度假胜地之一，以其白色沙滩、清澈海水和丰富的水上活动而闻名。岛上有多个海滩区域，如芭东海滩、卡塔海滩和卡伦海滩等。普吉岛的美食也非常有名，尤其是泰式海鲜料理。游客可以参观大佛、查龙寺等文化景点，也可以体验泰式按摩和夜市购物。住宿选择从经济型旅馆到豪华度假村应有尽有，交通可以选择出租车、嘟嘟车或租摩托车。"
KEYWORD_EXTRACTION_SAMPLE_OUTPUT = "芭东海滩景点, 普吉岛泰式海鲜餐厅, 查龙寺开放时间"

def get_keyword_extraction_messages(search_result: str) -> List:
    """获取从搜索结果中提取关键词的消息列表"""
    return [
        SystemMessage(content=KEYWORD_EXTRACTION_PROMPT),
        HumanMessage(content=KEYWORD_EXTRACTION_SAMPLE_INPUT),
        AIMessage(content=KEYWORD_EXTRACTION_SAMPLE_OUTPUT),
        HumanMessage(content=f"搜索结果: {search_result}")
    ]


# 评估搜索结果是否包含特定地点信息的提示词
RESULT_EVALUATION_PROMPT = """
请评估搜索结果是否包含关于特定的、可行动的、可以访问的地点信息。

特定地点是指类似"位于123号大街的XYZ餐厅"或"ABC公园，樱花观赏时间为上午9点至下午5点"这样的信息。
非特定地点是指类似"市中心区域"或"东京的餐厅"这样没有具体名称或地址的笼统描述。

根据这个标准，搜索结果是否包含特定地点信息？
只需回答"Yes"或"No"。
"""

# 示例输入和输出
RESULT_EVALUATION_SAMPLE_INPUT = "芭东海滩位于普吉岛西海岸，是岛上最热闹的海滩，长约3公里。这里有细腻的白沙和清澈的海水，是游泳、日光浴和水上运动的理想场所。海滩沿线有众多餐厅、酒吧和购物中心，如江西冷购物中心。最佳游览时间是11月至4月的旱季。可以从普吉镇乘坐公共巴士或出租车前往，车程约30分钟。海滩上有遮阳伞和躺椅出租，价格约为200泰铢/天。"
RESULT_EVALUATION_SAMPLE_OUTPUT = "Yes"

def get_result_evaluation_messages(search_result: str) -> List:
    """获取评估搜索结果是否包含特定地点信息的消息列表"""
    return [
        SystemMessage(content=RESULT_EVALUATION_PROMPT),
        HumanMessage(content=RESULT_EVALUATION_SAMPLE_INPUT),
        AIMessage(content=RESULT_EVALUATION_SAMPLE_OUTPUT),
        HumanMessage(content=f"搜索结果: {search_result}")
    ]


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


# 制定搜索计划的提示词
PLANNING_PROMPT = """
你是一个专业的规划助手。请根据提供的概览信息，制定一个详细的规划和搜索策略。

你需要：
1. 分析概览信息中提到的主要元素
2. 考虑时间、空间和逻辑关系，合理安排活动顺序
3. 为每个需要深入了解的项目生成精确的搜索关键词

以json作为输出格式，包含以下字段：
- search_plan: 进行搜索获取信息的计划
- keywords: 计划中所有需要搜索的关键词列表
"""

# 单地旅游规划示例
PLANNING_SAMPLE_INPUT_1 = """
京都是日本最受欢迎的旅游目的地之一，以其传统文化和历史景点闻名。主要景点包括清水寺、金阁寺和伏见稻荷大社等。京都的樱花季通常在3-4月，是最佳旅游季节。除了传统景点，京都还以美食闻名，如怀石料理和抹茶甜点。游客可以在祗园地区体验艺伎文化，或在岚山地区欣赏竹林和温泉。交通方面，可以使用地铁和公交车，或者租自行车游览。"""

PLANNING_SAMPLE_OUTPUT_1 = """{
    "thinking_process": "根据概览信息，京都的景点主要分布在东部（清水寺）、北部（金阁寺）和南部（伏见稻荷），建议按区域划分游玩顺序。考虑到游客体力和交通时间，每天安排2-3个主要景点，穿插美食和文化体验。",
    "search_plan": [
        {
            "天数": "第一天",
            "行程": [
                {
                    "时间": "上午",
                    "活动": "清水寺及周边古街",
                    "搜索关键词": "清水寺开放时间 门票"
                },
                {
                    "时间": "下午",
                    "活动": "祗园艺伎街",
                    "搜索关键词": "祗园艺伎表演预约"
                },
                {
                    "时间": "晚上",
                    "活动": "怀石料理晚餐",
                    "搜索关键词": "京都米其林怀石料理"
                }
            ]
        }
    ]
    "keywords": ["清水寺", "祗园艺伎", "怀石料理", "丽江古城", "黑龙潭", "古城酒吧"]

}"""

# 多地旅游规划示例
PLANNING_SAMPLE_INPUT_3 = """
云南是中国最受欢迎的旅游目的地之一，以其多元文化和自然风光闻名。主要旅游地包括丽江和大理。丽江以古城、玉龙雪山和老城酒吧闻名，可以体验纳西文化和高原风光。大理古城保存着白族文化，洛者古镇和苏海古生村都是特色景点。洛者古镇以天空之镜和特色小吃闻名。当地美食包括过桥米线、水晶饼等。交通方面，可以使用高铁或飞机在主要城市间移动。"""

PLANNING_SAMPLE_OUTPUT_3 = """{
    "thinking_process": "云南行程需要先划分主要目的地（丽江、大理），再根据各地特色景点和交通时间安排具体行程。考虑到高原适应和距离因素，建议每个地区停留2-3天，并在景点间适当安插美食体验。",
    "search_plan": [
        {
            "地区": "丽江",
            "天数": "第一天",
            "行程": [
                {
                    "时间": "上午10:00",
                    "活动": "丽江古城广场和四方街",
                    "搜索关键词": "丽江古城必去景点 人流量"
                },
                {
                    "时间": "下午14:00",
                    "活动": "黑龙潭徒步",
                    "搜索关键词": "黑龙潭徒步线路 门票"
                },
                {
                    "时间": "晚上19:00",
                    "活动": "古城酒吧街夜游",
                    "搜索关键词": "丽江酒吧街推荐 消费"
                }
            ]
        },
        {
            "地区": "大理",
            "天数": "第四天",
            "行程": [
                {
                    "时间": "上午09:00",
                    "活动": "大理古城游览",
                    "搜索关键词": "大理古城入城门票 导游"
                },
                {
                    "时间": "下午13:30",
                    "活动": "洛者古镇半日游",
                    "搜索关键词": "洛者古镇环湖公路 天空之镜"
                },
                {
                    "时间": "晚上18:00",
                    "活动": "洛者特色美食",
                    "搜索关键词": "洛者古镇美食街 必吃"
                }
            ]
        }
    ],
    "keywords": ["丽江古城", "黑龙潭", "古城酒吧", "大理古城", "洛者古镇", "天空之镜"]
}"""

# 美食探店示例
PLANNING_SAMPLE_INPUT_2 = """
"上海南京路上的美食店铺有：小杨生煎、老正兴、德兴楼、日料店「Sushi Express」和「Sushi Hiroba」等。多家美食店都需要提前排队。周边还有多家特色咖啡馆和甲级写字楼。周末人流量很大，建议选择工作日前往。 #南京路 #美食探店 #上海"
"""

PLANNING_SAMPLE_OUTPUT_2 = """{
    "thinking_process": "南京路美食众多，需要合理规划用餐时间和排队策略。考虑到人流量和等位时间，建议在工作日访问，并将热门店铺安排在非用餐高峰期。",
    "search_plan": [
        "日料":[
            "Sushi Express",
            "Sushi Hiroba"
        ]
        "小吃":[
            "小杨生煎",
        ]
        "面食":[
            "老正兴",
            "德兴楼"
        ]
    "keywords": ["Sushi Express", "Sushi Hiroba", "小杨生煎", "老正兴", "德兴楼"]
}"""


def get_planning_messages(overview: str) -> List:
    """获取制定计划的消息列表"""
    return [
        SystemMessage(content=PLANNING_PROMPT),
        HumanMessage(content=PLANNING_SAMPLE_INPUT_1),
        AIMessage(content=PLANNING_SAMPLE_OUTPUT_1),
        HumanMessage(content=PLANNING_SAMPLE_INPUT_2),
        AIMessage(content=PLANNING_SAMPLE_OUTPUT_2),
        HumanMessage(content=PLANNING_SAMPLE_INPUT_3),
        AIMessage(content=PLANNING_SAMPLE_OUTPUT_3),
        HumanMessage(content=overview)
    ]