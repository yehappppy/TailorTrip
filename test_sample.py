from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import time

from src.llm_agent.sample.sample_chatbot import run_with_chat, run_with_fast, run_with_thinking



start_time = time.time()
query = "仔细思考，为什么天是蓝色的?"
response = run_with_chat(query)
print(f">>> This is the single chat model (run in {time.time()-start_time}s):")
print(response) # response should be a AIMessage with content=the ai generated answer

start_time = time.time()
query = "仔细思考，为什么天是蓝色的?"
response = run_with_fast(query)
print(f">>> This is the fast chat model (run in {time.time()-start_time}s):")
print(response) # response should be a AIMessage with content=the ai generated answer

# query = "十减五等于几？"
# response = run_with_tools(query)
# print(">>> This is llm bind with tools:")
# print(response) # response should be a AIMessage with content="" (in this case tools are invoked)

query = "仔细思考，为什么天是蓝色的?"
response = run_with_thinking(query)
print(">>> This is the thinking model:")
print(response) # response should be a AIMessage with content=the ai generated answer