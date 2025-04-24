from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from typing import List, Dict, Any

from src.utils.llm import base_llm
from src.utils.util import structure_output

SEARCH_INFORMATION_PROMPT = """
你要假装成为一个搜索引擎。根据用户给定的关键词，你需要：
1. 根据关键词编撰出一篇推文
2. 确保信息与用户的关键词相关
3. 推文中应当包含具体的细节，每次回答的结果相互独立

请直接进行输出：
"""

SAMPLE_INPUT = """
日本京都樱花季
"""

SAMPLE_OUTPUT = """
🌸 京都樱花季攻略来啦！2024年预测花期：3月25日-4月5日，比往年稍早！最佳赏樱地：
1️⃣ 哲学之道：2公里樱花隧道，夜樱点灯超梦幻
2️⃣ 岚山竹林：樱花与竹林的绝妙组合
3️⃣ 清水寺：千年古刹+粉色樱花=绝美明信片风景

🏨 住宿建议：祗园附近传统町屋，人均¥800/晚，可体验茶道和和服

🚆 交通贴士：推荐购买"京都巴士一日券"（¥700），无限次乘坐！

⚠️ 注意：热门景点需提前1个月预约，特别是怀石料理餐厅！#京都旅行 #樱花季
"""

def search_information(keyword: str) -> List[Dict[str, Any]]:
    llm = base_llm()
    messages = [
        SystemMessage(content=SEARCH_INFORMATION_PROMPT),
        HumanMessage(content=SAMPLE_INPUT),
        AIMessage(content=SAMPLE_OUTPUT),
        HumanMessage(content=keyword)
    ]
    result = llm.invoke(messages).content
    return [result]