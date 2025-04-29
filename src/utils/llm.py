import os
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek

from .util import load_config

config = load_config()["llm_configuration"]

def base_llm():
    # in most of time using ChatOpenAI as standard llm invoker
    llm = ChatOpenAI(
        model="Qwen/Qwen2.5-72B-Instruct",
        temperature=0,
        base_url=config["llm_base_url"],
        api_key=config["llm_api_key"]
    )
    return llm

def fast_llm():
    # in most of time using ChatOpenAI as standard llm invoker
    llm = ChatOpenAI(
        model="Qwen/Qwen2.5-14B-Instruct",
        temperature=0,
        base_url=config["llm_base_url"],
        api_key=config["llm_api_key"]
    )
    return llm

def cot_llm():
    # when the llm has reasoning, only ChatDeepSeek could retrieve reasoning_content
    llm = ChatDeepSeek(
        model="Qwen/QwQ-32B",
        temperature=0,
        api_base=config["llm_base_url"],
        api_key=config["llm_api_key"]
    )
    return llm
