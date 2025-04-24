from langchain_core.messages import HumanMessage, SystemMessage

from src.utils.llm import base_llm, cot_llm
from src.tools.retrieve import retrieve
from src.tools.calculate import add, minus, divide, multiply

SYS_PROMPT_CHAT = """
You are a helpful assistant to answer whatever user want to know.
"""

SYS_PROMPT_RETRIEVER = """
You are a helpful assistant to retrieve relevant document given user input.
"""

def run_with_chat(query):
    llm = base_llm()
    messages = [
        SystemMessage(content=SYS_PROMPT_RETRIEVER),
        HumanMessage(content=query)
    ]
    response = llm.invoke(messages)
    return response

def run_with_tools(query):
    tools = [retrieve, add, minus, divide, multiply]
    llm = base_llm()
    llm = llm.bind_tools(tools)
    messages = [
        SystemMessage(content=SYS_PROMPT_RETRIEVER),
        HumanMessage(content=query)
    ]
    response = llm.invoke(messages)
    return response

def run_with_thinking(query):
    llm = cot_llm()
    messages = [
        SystemMessage(content=SYS_PROMPT_RETRIEVER),
        HumanMessage(content=query)
    ]
    response = llm.invoke(messages)
    return response

def run_with_stream(query):
    llm = base_llm()
    messages = [
        SystemMessage(content=SYS_PROMPT_RETRIEVER),
        HumanMessage(content=query)
    ]
    for message_chunk in llm.stream(messages):
        print(message_chunk.content, end="", flush=True)










