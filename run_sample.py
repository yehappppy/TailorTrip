from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from src.llm_agent.sample_chatbot import run_with_tools, run_with_chat, run_with_thinking

query = "你今天过得好吗?"
response = run_with_chat(query)
print(">>> This is the single chat model:")
print(response) # response should be a AIMessage with content=the ai generated answer

query = "十减五等于几？"
response = run_with_tools(query)
print(">>> This is llm bind with tools:")
print(response) # response should be a AIMessage with content="" (in this case tools are invoked)

query = "仔细思考，为什么天是蓝色的?"
response = run_with_thinking(query)
print(">>> This is the thinking model:")
print(response) # response should be a AIMessage with content=the ai generated answer