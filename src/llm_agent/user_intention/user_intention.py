import json
import re
import sys
import os

# Add the parent directory of 'src' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.utils.llm import base_llm, cot_llm


def call_llm(messages, model_choice="base"):

    if model_choice == "cot":
        llm = cot_llm()
    else:
        llm = base_llm()
    
    formatted_messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in messages
    ]
    response = llm.invoke(formatted_messages)
    
    return response.content.strip()

def clean_json(text):
    return re.sub(r"```json|```", "", text).strip()


# Safety
def llm_safety_check(text):
    safety_prompt = [
        {
            "role": "system",
            "content": """你是一位用户输入信息安全检测专家。请严格判断以下内容是否包含以下风险：
            1. 违法/危险行为
            2. 人身伤害/自残建议
            3. 诈骗/钓鱼信息
            4. 仇恨/歧视言论
            5. 敏感政治话题
            请严格地返回JSON：{"safe": true/false, "reason": "检测依据（20字内）"}"""
        },
        {
            "role": "user",
            "content": text
        }
    ]

    response = call_llm(safety_prompt)
    result = json.loads(clean_json(response))
    
    if "safe" not in result or "reason" not in result:
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
            {
                "role": "system",
                "content": """# 你是一个旅游推荐系统的AI小助手，请根据输入完成以下两个任务：
                
                任务1：根据提取的信息生成最可能的完整查询意图：
                1. 优先补全景点类需求（游玩时间/门票/预算）
                2. 其次补全餐饮类需求（预算/人数/忌口）
                3. 其他可能的详细搜索内容
                4. 用户意图已完整则返回原输入

                任务2：提取以下用户偏好信息：
                - 地点（必填）
                - 人数（必填，数字）
                - 用餐标准/旅游规格标准（必填，格式如"100每人"）
                - 排除餐厅/景点（可选）
                - 旅游时长（可选，格式如“几天几晚”）
                - 其他出现的跟查询相关的关键信息（例如提到夜市、小吃等）
                请确保每一项偏好都被明确命名分类，不使用“其他”。
                
                请严格返回JSON格式，包含两个字段：
                - "guess": 生成的完整查询意图
                - "preference": 提取的用户偏好信息
                
                示例：
                输入："迪士尼"
                输出：{
                    "guess": "迪士尼两人门票价格和游玩时间",
                    "preference": {"地区":"迪士尼","人数":"2","标准":"500每人"}
                }
                
                输入："中环 3人"
                输出：{
                    "guess": "中环3人预算300每人一日游",
                    "preference": {"地区":"中环","人数":"3","标准":"300每人", "时长":"一日游"}
                }"""
            },
            {
                "role": "user",
                "content": f"当前输入：{context}"
            }
        ]

        response = call_llm(messages, model_choice="cot")
        result = json.loads(clean_json(response))
        
        # Store the extracted preference
        if "preference" in result:
            self.preference = result["preference"]
        
        return result.get("guess", context)


    def interactive_guess(self, initial_input: str, chat_history: list) -> tuple:
        current_context = initial_input
        
        while self.attempt_count < self.max_attempts:
            guessed_query = self.generate_guess(current_context)
            self.attempt_count += 1
            
            print(f"[系统猜测] 您是否在查找：{guessed_query}？(是/否/补充信息)")
            user_feedback = input("用户反馈：").strip()
            
            self.guess_and_feedback.append({
            "system_guess": guessed_query,
            "user_feedback": user_feedback
        })
            if user_feedback.lower() in ["是", "是的","对","没错", "yes", "y"]:
                return True, guessed_query
            elif user_feedback.lower() in ["否", "不对","不是", "错误", "no", "n"]:
                current_context = initial_input
            else:
                current_context = f"{current_context} {user_feedback}"  
        
        return False, current_context
    

 
# Flag
class FlagClassifier:
    def __init__(self, chat_history=[]):
        self.chat_history = chat_history[-3:]
    
    def _build_classification_prompt(self, current_query):

        history_str = "\n".join([f"{msg['role']}: {msg['content']}" 
                               for msg in self.chat_history])
        # print(history_str)
        
        return [
            {"role": "system", "content": f"""# Flag分类标准：
             A类（可根据历史对话直接回答、或常识类的简单问题）；
             B类（需要查询小红书平台内容数据）；
             C类（需要复杂逻辑推理。
             当前对话历史：{history_str if history_str else "无历史对话"}
             请严格按以下JSON格式响应：{{"flag": "A/B/C", "reason": "分类原因"}}"""},
            {"role": "user", "content": f"待分类问题：{current_query}"}
        ]

    def classify(self, current_query):
        try:
            messages = self._build_classification_prompt(current_query)
            response = call_llm(messages)
            
            cleaned = clean_json(response)
            result = json.loads(cleaned)
            if result["flag"] not in ("A", "B", "C"):
                raise ValueError("Invalid flag value")
                
            return result
            
        except Exception as e:
            print(f"分类失败：{str(e)}")
            return {"flag": "D", "reason": "无法分类"}


# overall workflow
def process_query(user_input, chat_history=[]):
    # safety check
    is_safe, reason = llm_safety_check(user_input)
    if not is_safe:
        return {"status": "blocked", "reason": reason}

    # user intent
    completer = IntentCompleter()
    validation_status, final_query = completer.interactive_guess(user_input, chat_history)
    
    if not validation_status:
        return {"status": "unconfirmed", "original": user_input}

    # flag classification
    classifier = FlagClassifier(chat_history)
    classification = classifier.classify(final_query)

    return {
        "status": "confirmed",
        "original": user_input,
        "final_query": final_query,
        "flag": classification["flag"],
        "reason": classification["reason"],
        "preference": completer.preference,  # Use the stored preference
        "difficulty": classification["flag"],
        "has_end": "Yes"
    }

if __name__ == "__main__":
    chat_history = []
    all_records = []
    while True:
        query = input("\n请输入您的查询（输入exit退出查询）：").strip()
        if query.lower() == "exit":
            break
        result = process_query(query, chat_history)

        if result["status"] == "blocked":
            print(f"内容不安全：{result['reason']}")
        elif result["status"] == "unconfirmed":
            print("需求未确认，请重新描述")
        else:
            print(f"确认需求：{result['final_query']}")
            print(f"分类标记：{result['flag']}（{result['reason']}）")
            
            chat_history.append({"role": "user", "content": result['final_query']})
            all_records.append({
                "preference": result["preference"],
                "difficulty": result["difficulty"],
                "has_end": result["has_end"]
            })
    print("\n最终所有记录：")
    for record in all_records:
        print(record)