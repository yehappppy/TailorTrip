__author__ = "yh"
__date__ = "2025-04-11"
__description__ = "Customized LLM for symptom prediction"

import openai
from openai import OpenAI
from langchain.llms.base import LLM
from pydantic import BaseModel, Field
from typing import Dict, List, Optional

openai.api_request_timeout = 10  # set timeout to 10 seconds

class OpenAILLM(LLM, BaseModel):
    config: Dict = Field(...)  # use Field to declare required config fields
    
    class Config:
        arbitrary_types_allowed = True  # allow arbitrary types
    
    @property
    def _llm_type(self) -> str:
        return "openai"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        client = OpenAI(api_key=self.config["api_key"], base_url=self.config["base_url"])
        messages = [
            {
                "role": "system",
                "content": self.config["system_input"]
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        # call OpenAI API Streaming
        response = client.chat.completions.create(
            model=self.config["model_name"],
            messages=messages,
            max_tokens=self.config.get("max_tokens", None),
            temperature=self.config.get("temperature", 1.0),
            top_p=self.config.get("top_p", 1.0),
            tools=self.config.get("tools", None),
            tool_choice=self.config.get("tool_choice", "auto"),
            stream=True
        )

        # process streaming output
        output = ""
        thinking_started = False
        thinking_ended = False
        for chunk in response:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            # This is not supported by OpenAI library but is used in DeepSeek and SiliconFlow API
            if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                if not thinking_started:
                    output += "<think>"
                    thinking_started = True
                output += delta.reasoning_content
                print(delta.reasoning_content, end="", flush=True)
            elif thinking_started and not thinking_ended:
                output += "</think>"
                thinking_ended = True
            # This is the standard OpenAI library
            if delta.content:
                output += delta.content
                print(delta.content, end="", flush=True)

        return output

