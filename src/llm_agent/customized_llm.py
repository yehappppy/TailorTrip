"""
Customized LLM implementation for TailorTrip.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union
import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class OpenAILLM:
    """
    OpenAI LLM implementation for TailorTrip.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the OpenAI LLM with configuration.
        
        Args:
            config: Configuration dictionary with api_key, base_url, model_name, etc.
        """
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", "https://api.openai.com/v1")
        self.model_name = config.get("model_name", "gpt-4")
        self.max_tokens = config.get("max_tokens", 8192)
        self.temperature = config.get("temperature", 0.0)
        self.system_input = config.get("system_input", "")
        
        if not self.api_key:
            raise ValueError("API key is required for OpenAI LLM")
        
        # Initialize session
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        })
        
    def _call(self, user_input: str) -> str:
        """
        Call the OpenAI API with the given user input.
        
        Args:
            user_input: The user's input text
            
        Returns:
            The LLM's response as a string
        """
        messages = []
        
        # Add system message if provided
        if self.system_input:
            messages.append({"role": "system", "content": self.system_input})
        
        # Add user message
        messages.append({"role": "user", "content": user_input})
        
        try:
            payload = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except RequestException as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise Exception(f"Failed to get response from LLM: {str(e)}")
