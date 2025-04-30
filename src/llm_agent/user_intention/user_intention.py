import sys
import os
import json
import re
from typing import Dict, List, Optional, Tuple, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Add the parent directory of 'src' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.utils.util import structure_output
from src.utils.llm import base_llm, cot_llm


# Prompts and examples
USER_INTENTION_PROMPT = """
你是一个旅游查询意图理解助手。你需要理解用户的旅游查询需求，并提取关键信息。

输出格式要求：
{
    "guess": "对用户查询的完整理解",
    "preference": {
        "地区": "查询涉及的地区",
        "人数": "出行人数",
        "标准": "预算标准",
        "时长": "游玩时长"
    }
}
"""

SAMPLE_INPUT1 = "我想去中环玩，大概3个人，预算每人300，就玩一天"

SAMPLE_OUTPUT1 = """{
    "guess": "中环3人预算300每人一日游",
    "preference": {"地区":"中环","人数":"3","标准":"300每人", "时长":"一日游"}
}"""

SAMPLE_INPUT2 = "想去迪士尼，两个人，玩2天1夜"

SAMPLE_OUTPUT2 = """{
    "guess": "迪士尼2人2天1夜游",
    "preference": {"地区":"迪士尼","人数":"2","标准":"", "时长":"2天1夜"}
}"""

SAFETY_CHECK_PROMPT = """你是一位用户输入信息安全检测专家。请严格判断以下内容是否包含以下风险：
1. 违法/危险行为
2. 人身伤害/自残建议
3. 诈骗/钓鱼信息
4. 仇恨/歧视言论
5. 敏感政治话题

请严格地返回JSON：{"safe": true/false, "reason": "检测依据（20字内）"}
"""

SAMPLE_SAFETY_INPUT1 = "我想去迪士尼玩"

SAMPLE_SAFETY_OUTPUT1 = """{
    "safe": true,
    "reason": "正常的旅游咨询"
}"""

SAMPLE_SAFETY_INPUT2 = "我想去某些不合法的地方玩"

SAMPLE_SAFETY_OUTPUT2 = """{
    "safe": false,
    "reason": "涉及违法地点"
}"""

FLAG_CLASSIFICATION_PROMPT = """
# Flag分类标准：
A类（可根据历史对话直接回答、或常识类的简单问题）；
B类（需要查询小红书平台内容数据）；
C类（需要复杂逻辑推理）。

请严格按以下JSON格式响应：{"flag": "A/B/C", "reason": "分类原因"}
"""

SAMPLE_CLASSIFICATION_INPUT1 = "迪士尼门票多少钱"

SAMPLE_CLASSIFICATION_OUTPUT1 = """{
    "flag": "A",
    "reason": "门票价格是常见问题，可直接回答"
}"""

SAMPLE_CLASSIFICATION_INPUT2 = "帮我规划一个三天两夜的旅游行程"

SAMPLE_CLASSIFICATION_OUTPUT2 = """{
    "flag": "C",
    "reason": "需要复杂的行程规划和推理"
}"""

# Safety
def llm_safety_check(text):
    messages = [
        SystemMessage(content=SAFETY_CHECK_PROMPT),
        HumanMessage(content=SAMPLE_SAFETY_INPUT1),
        AIMessage(content=SAMPLE_SAFETY_OUTPUT1),
        HumanMessage(content=SAMPLE_SAFETY_INPUT2),
        AIMessage(content=SAMPLE_SAFETY_OUTPUT2),
        HumanMessage(content=text)
    ]
    llm = base_llm()
    response = llm.invoke(messages).content
    result = structure_output(response)
    
    if not result or "safe" not in result or "reason" not in result:
        raise ValueError("Invalid response format")
        
    return result["safe"], result["reason"]


# User intent
class IntentCompleter:
    def __init__(self):
        self.max_attempts = 5
        self.attempt_count = 0
        self.guess_and_feedback = []
        self.preference = {}

    def generate_guess(self, context: str) -> str:
        messages = [
            SystemMessage(content=USER_INTENTION_PROMPT),
            HumanMessage(content=SAMPLE_INPUT1),
            AIMessage(content=SAMPLE_OUTPUT1),
            HumanMessage(content=SAMPLE_INPUT2),
            AIMessage(content=SAMPLE_OUTPUT2),
            HumanMessage(content=context)
        ]
        llm = base_llm()
        response = llm.invoke(messages).content
        result = structure_output(response)
        
        # Store the extracted preference
        if result and "preference" in result:
            self.preference = result["preference"]
        
        return result.get("guess", context) if result else context

    def _build_context(self, user_input: str, chat_history: List, guess_and_feedback: List = None) -> str:
        history_str = "\n".join([f"{msg['role']}: {msg['content']}" 
                               for msg in chat_history])
        
        if guess_and_feedback:
            guess_and_feedback_str = "\n".join([f"系统猜测：{msg['guess']}\n用户反馈：{msg['feedback']}" 
                                              for msg in guess_and_feedback])
            return f"{history_str}\n{guess_and_feedback_str}\n{user_input}"
        else:
            return f"{history_str}\n{user_input}"

    def interactive_guess(self, user_input: str, chat_history: List) -> Tuple[bool, str]:
        context = self._build_context(user_input, chat_history)
        guess = self.generate_guess(context)
        
        while self.attempt_count < self.max_attempts:
            self.attempt_count += 1
            self.guess_and_feedback.append({"guess": guess})
            
            # 如果是测试环境，自动确认
            if "__test__" in globals():
                print(f"[系统猜测] 您是否在查找：{guess}(是/否/补充信息)")
                feedback = "是"
                print(f"用户反馈：{feedback}")
            else:
                feedback = input(f"[系统猜测] 您是否在查找：{guess}(是/否/补充信息)\n用户反馈：")
            
            self.guess_and_feedback[-1]["feedback"] = feedback
            
            if feedback.lower() == "是":
                return True, guess
            elif feedback.lower() == "否":
                if self.attempt_count >= self.max_attempts:
                    break
                context = self._build_context(user_input, chat_history, self.guess_and_feedback)
                guess = self.generate_guess(context)
            else:  # 用户提供了补充信息
                context = self._build_context(feedback, chat_history, self.guess_and_feedback)
                guess = self.generate_guess(context)
    

 
FLAG_CLASSIFICATION_PROMPT = """
# Flag分类标准：
A类（可根据历史对话直接回答、或常识类的简单问题）；
B类（需要查询小红书平台内容数据）；
C类（需要复杂逻辑推理）。

请严格按以下JSON格式响应：{"flag": "A/B/C", "reason": "分类原因"}
"""

SAMPLE_CLASSIFICATION_INPUT1 = "迪士尼门票多少钱"

SAMPLE_CLASSIFICATION_OUTPUT1 = """{
    "flag": "A",
    "reason": "门票价格是常见问题，可直接回答"
}"""

SAMPLE_CLASSIFICATION_INPUT2 = "帮我规划一个三天两夜的旅游行程"

SAMPLE_CLASSIFICATION_OUTPUT2 = """{
    "flag": "C",
    "reason": "需要复杂的行程规划和推理"
}"""

# Flag
class FlagClassifier:
    def __init__(self, chat_history=[]):
        self.chat_history = chat_history[-3:]
    
    def _build_classification_prompt(self, current_query):
        history_str = "\n".join([f"{msg['role']}: {msg['content']}" 
                               for msg in self.chat_history])
        
        system_content = FLAG_CLASSIFICATION_PROMPT
        if history_str:
            system_content += f"\n当前对话历史：\n{history_str}"
        
        return [
            SystemMessage(content=system_content),
            HumanMessage(content=SAMPLE_CLASSIFICATION_INPUT1),
            AIMessage(content=SAMPLE_CLASSIFICATION_OUTPUT1),
            HumanMessage(content=SAMPLE_CLASSIFICATION_INPUT2),
            AIMessage(content=SAMPLE_CLASSIFICATION_OUTPUT2),
            HumanMessage(content=f"待分类问题：{current_query}")
        ]

    def classify(self, current_query):
        try:
            messages = self._build_classification_prompt(current_query)
            llm = base_llm()
            response = llm.invoke(messages)
            
            result = structure_output(response.content)
            if not result or result["flag"] not in ("A", "B", "C"):
                raise ValueError("Invalid flag value")
                
            return result
            
        except Exception as e:
            print(f"分类失败：{str(e)}")
            return {"flag": "D", "reason": "无法分类"}


# overall workflow
def process_user_input(user_input: str, chat_history: List = None) -> Dict[str, Any]:
    """处理用户输入，包括安全检查、意图理解和分类
    
    Args:
        user_input: 用户输入的原始文本
        chat_history: 聊天历史记录，用于上下文理解
        
    Returns:
        Dict[str, Any]: 包含以下键的字典：
            - status: 处理状态（confirmed/unconfirmed/blocked）
            - original: 原始输入
            - final_query: 补全后的查询（如果status为confirmed）
            - flag: 查询类型（如果status为confirmed）
            - reason: 原因说明
            - preference: 用户偏好（如果status为confirmed）
    """
    if chat_history is None:
        chat_history = []
        
    # 1. 安全检查
    is_safe, reason = llm_safety_check(user_input)
    if not is_safe:
        return {"status": "blocked", "reason": reason}

    # 2. 意图理解
    completer = IntentCompleter()
    validation_status, final_query = completer.interactive_guess(user_input, chat_history)
    
    if not validation_status:
        return {"status": "unconfirmed", "original": user_input}

    # 3. 查询分类
    classifier = FlagClassifier(chat_history)
    classification = classifier.classify(final_query)

    # 4. 返回结果
    return {
        "status": "confirmed",
        "original": user_input,
        "final_query": final_query,
        "flag": classification["flag"],
        "reason": classification["reason"],
        "preference": completer.preference
    }

if __name__ == "__main__":
    chat_history = []
    while True:
        query = input("\n请输入您的查询（输入exit退出查询）：").strip()
        if query.lower() == "exit":
            break
            
        result = process_user_input(query, chat_history)

        if result["status"] == "blocked":
            print(f"内容不安全：{result['reason']}")
        elif result["status"] == "unconfirmed":
            print("需求未确认，请重新描述")
        else:
            print(f"确认需求：{result['final_query']}")
            print(f"分类标记：{result['flag']}（{result['reason']}）")
            print(f"用户偏好：{result['preference']}")
            
            chat_history.append({"role": "user", "content": result['final_query']})