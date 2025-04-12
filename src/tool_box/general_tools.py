"""
General tools implementation for TailorTrip.
These tools extend the MCPToolbox to provide common functionality.
"""

import json
import os
import requests
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from src.tool_box.mcp_toolbox import MCPToolbox, MCPConfig, MCPError, Role

logger = logging.getLogger(__name__)

class GeneralTools(MCPToolbox):
    """
    Implementation of general tools extending the MCPToolbox.
    """
    
    def __init__(self, config: MCPConfig):
        """Initialize with MCPConfig."""
        super().__init__(config)
        self.vector_store_path = os.getenv('VECTOR_STORE_PATH', './data/vector_store')
        self.embeddings = None
        self.vector_store = None
        
    async def _execute_single_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        Execute a single tool with proper validation and execution.
        
        Args:
            tool_name: Name of the tool to execute
            args: Arguments for the tool
            
        Returns:
            Result of the tool execution
        """
        tool_mapping = {
            "web_search": self.web_search,
            "web_scrape": self.web_scrape,
            "weather_info": self.weather_info,
            "currency_convert": self.currency_convert,
            "save_to_vector_store": self.save_to_vector_store,
            "query_vector_store": self.query_vector_store,
            "image_search": self.image_search,
            "summarize_text": self.summarize_text
        }
        
        if tool_name not in tool_mapping:
            raise MCPError(f"Unknown tool: {tool_name}")
            
        return await tool_mapping[tool_name](**args)
    
    async def web_search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Perform a web search for the given query.
        
        Args:
            query: Search query
            num_results: Number of results to return (default: 5)
            
        Returns:
            List of search results with title, url, and snippet
        """
        # Note: In a production environment, you would use a real search API
        # This is a simplified implementation for demonstration
        try:
            # Using a mock search API for demonstration
            search_url = f"https://api.duckduckgo.com/?q={query}&format=json"
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url) as response:
                    if response.status != 200:
                        raise MCPError(f"Search API returned status {response.status}")
                    
                    data = await response.json()
                    results = []
                    
                    # Process results (simplified)
                    for i, result in enumerate(data.get("RelatedTopics", [])[:num_results]):
                        if "Text" in result and "FirstURL" in result:
                            results.append({
                                "title": result["Text"].split(" - ")[0],
                                "url": result["FirstURL"],
                                "snippet": result["Text"]
                            })
                    
                    return results
        except Exception as e:
            logger.error(f"Error in web search: {str(e)}")
            raise MCPError(f"Web search failed: {str(e)}")
    
    async def web_scrape(self, url: str, elements_to_extract: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Scrape content from a webpage.
        
        Args:
            url: URL to scrape
            elements_to_extract: List of HTML elements to extract (e.g., ["h1", "p", "img"])
                If None, extracts main text content
                
        Returns:
            Dictionary with extracted content
        """
        if elements_to_extract is None:
            elements_to_extract = ["h1", "h2", "h3", "p"]
            
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        raise MCPError(f"Failed to fetch URL: {url}, status: {response.status}")
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    result = {
                        "url": url,
                        "timestamp": datetime.utcnow().isoformat(),
                        "title": soup.title.text if soup.title else "",
                        "content": {}
                    }
                    
                    # Extract requested elements
                    for element in elements_to_extract:
                        elements = soup.find_all(element)
                        result["content"][element] = [elem.get_text(strip=True) for elem in elements]
                    
                    # Get main text content
                    main_content = " ".join([p.get_text(strip=True) for p in soup.find_all("p")])
                    result["main_content"] = main_content[:5000]  # Limit to 5000 chars
                    
                    return result
        except Exception as e:
            logger.error(f"Error in web scrape: {str(e)}")
            raise MCPError(f"Web scrape failed: {str(e)}")
    
    async def weather_info(self, location: str) -> Dict[str, Any]:
        """
        Get weather information for a location.
        
        Args:
            location: Location to get weather for
            
        Returns:
            Weather information
        """
        # Note: In a production environment, you would use a real weather API
        # This is a simplified implementation for demonstration
        try:
            # Using a mock weather API for demonstration
            api_key = os.getenv("WEATHER_API_KEY")
            if not api_key:
                # Return mock data if no API key
                return {
                    "location": location,
                    "timestamp": datetime.utcnow().isoformat(),
                    "temperature": 22,
                    "condition": "Sunny",
                    "humidity": 60,
                    "wind_speed": 10,
                    "forecast": [
                        {"day": "Today", "condition": "Sunny", "max": 25, "min": 18},
                        {"day": "Tomorrow", "condition": "Partly Cloudy", "max": 23, "min": 17}
                    ],
                    "note": "This is mock data for demonstration purposes"
                }
            
            # Real implementation would use the API key to fetch real data
            weather_url = f"https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days=3"
            async with aiohttp.ClientSession() as session:
                async with session.get(weather_url) as response:
                    if response.status != 200:
                        raise MCPError(f"Weather API returned status {response.status}")
                    
                    data = await response.json()
                    
                    # Process and format the weather data
                    current = data.get("current", {})
                    forecast = data.get("forecast", {}).get("forecastday", [])
                    
                    result = {
                        "location": location,
                        "timestamp": datetime.utcnow().isoformat(),
                        "temperature": current.get("temp_c"),
                        "condition": current.get("condition", {}).get("text"),
                        "humidity": current.get("humidity"),
                        "wind_speed": current.get("wind_kph"),
                        "forecast": []
                    }
                    
                    for day in forecast:
                        result["forecast"].append({
                            "day": day.get("date"),
                            "condition": day.get("day", {}).get("condition", {}).get("text"),
                            "max": day.get("day", {}).get("maxtemp_c"),
                            "min": day.get("day", {}).get("mintemp_c")
                        })
                    
                    return result
        except Exception as e:
            logger.error(f"Error in weather info: {str(e)}")
            raise MCPError(f"Weather info failed: {str(e)}")
    
    async def currency_convert(self, amount: float, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """
        Convert currency.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code (e.g., "USD")
            to_currency: Target currency code (e.g., "EUR")
            
        Returns:
            Conversion result
        """
        # Note: In a production environment, you would use a real currency API
        # This is a simplified implementation for demonstration
        try:
            # Using a mock currency API for demonstration
            api_key = os.getenv("CURRENCY_API_KEY")
            if not api_key:
                # Use fixed exchange rates for demonstration
                rates = {
                    "USD": 1.0,
                    "EUR": 0.93,
                    "GBP": 0.79,
                    "JPY": 150.2,
                    "CNY": 7.2,
                    "HKD": 7.8
                }
                
                if from_currency not in rates or to_currency not in rates:
                    raise MCPError(f"Currency not supported: {from_currency} or {to_currency}")
                
                # Convert using fixed rates
                usd_amount = amount / rates[from_currency]
                converted_amount = usd_amount * rates[to_currency]
                
                return {
                    "amount": amount,
                    "from_currency": from_currency,
                    "to_currency": to_currency,
                    "converted_amount": round(converted_amount, 2),
                    "rate": round(rates[to_currency] / rates[from_currency], 4),
                    "timestamp": datetime.utcnow().isoformat(),
                    "note": "This is based on fixed rates for demonstration purposes"
                }
            
            # Real implementation would use the API key to fetch real data
            currency_url = f"https://api.exchangerate.host/convert?from={from_currency}&to={to_currency}&amount={amount}"
            async with aiohttp.ClientSession() as session:
                async with session.get(currency_url) as response:
                    if response.status != 200:
                        raise MCPError(f"Currency API returned status {response.status}")
                    
                    data = await response.json()
                    
                    if not data.get("success"):
                        raise MCPError("Currency conversion failed")
                    
                    return {
                        "amount": amount,
                        "from_currency": from_currency,
                        "to_currency": to_currency,
                        "converted_amount": data.get("result"),
                        "rate": data.get("info", {}).get("rate"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
        except Exception as e:
            logger.error(f"Error in currency conversion: {str(e)}")
            raise MCPError(f"Currency conversion failed: {str(e)}")
    
    async def save_to_vector_store(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Save text to vector store for later retrieval.
        
        Args:
            text: Text to save
            metadata: Optional metadata to associate with the text
            
        Returns:
            Status of the operation
        """
        try:
            if metadata is None:
                metadata = {}
                
            # Add timestamp to metadata
            metadata["timestamp"] = datetime.utcnow().isoformat()
            
            # Initialize embeddings if not already done
            if self.embeddings is None:
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise MCPError("OpenAI API key is required for vector store operations")
                self.embeddings = OpenAIEmbeddings(api_key=api_key)
            
            # Initialize vector store if not already done
            if self.vector_store is None:
                self.vector_store = Chroma(
                    persist_directory=self.vector_store_path,
                    embedding_function=self.embeddings
                )
            
            # Split text into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=100
            )
            chunks = text_splitter.split_text(text)
            
            # Create documents
            documents = [
                Document(page_content=chunk, metadata=metadata)
                for chunk in chunks
            ]
            
            # Add documents to vector store
            ids = self.vector_store.add_documents(documents)
            
            # Persist vector store
            self.vector_store.persist()
            
            return {
                "status": "success",
                "message": f"Added {len(documents)} chunks to vector store",
                "ids": ids,
                "timestamp": metadata["timestamp"]
            }
        except Exception as e:
            logger.error(f"Error in save to vector store: {str(e)}")
            raise MCPError(f"Save to vector store failed: {str(e)}")
    
    async def query_vector_store(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Query the vector store for similar texts.
        
        Args:
            query: Query text
            k: Number of results to return
            
        Returns:
            List of similar documents with content and metadata
        """
        try:
            # Initialize embeddings if not already done
            if self.embeddings is None:
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise MCPError("OpenAI API key is required for vector store operations")
                self.embeddings = OpenAIEmbeddings(api_key=api_key)
            
            # Initialize vector store if not already done
            if self.vector_store is None:
                if not os.path.exists(self.vector_store_path):
                    raise MCPError("Vector store does not exist")
                    
                self.vector_store = Chroma(
                    persist_directory=self.vector_store_path,
                    embedding_function=self.embeddings
                )
            
            # Query vector store
            results = self.vector_store.similarity_search_with_score(query, k=k)
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": float(score)
                })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error in query vector store: {str(e)}")
            raise MCPError(f"Query vector store failed: {str(e)}")
    
    async def image_search(self, query: str, num_results: int = 3) -> List[Dict[str, str]]:
        """
        Search for images related to the query.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of image results with url, title, and source
        """
        # Note: In a production environment, you would use a real image search API
        # This is a simplified implementation for demonstration
        try:
            # Using a mock image search for demonstration
            api_key = os.getenv("IMAGE_SEARCH_API_KEY")
            if not api_key:
                # Return mock data
                return [
                    {
                        "url": f"https://example.com/image1_{query.replace(' ', '_')}.jpg",
                        "title": f"Image 1 for {query}",
                        "source": "example.com",
                        "note": "This is mock data for demonstration purposes"
                    },
                    {
                        "url": f"https://example.com/image2_{query.replace(' ', '_')}.jpg",
                        "title": f"Image 2 for {query}",
                        "source": "example.com",
                        "note": "This is mock data for demonstration purposes"
                    },
                    {
                        "url": f"https://example.com/image3_{query.replace(' ', '_')}.jpg",
                        "title": f"Image 3 for {query}",
                        "source": "example.com",
                        "note": "This is mock data for demonstration purposes"
                    }
                ][:num_results]
            
            # Real implementation would use the API key to fetch real data
            search_url = f"https://api.unsplash.com/search/photos?query={query}&per_page={num_results}"
            headers = {"Authorization": f"Client-ID {api_key}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=headers) as response:
                    if response.status != 200:
                        raise MCPError(f"Image search API returned status {response.status}")
                    
                    data = await response.json()
                    results = []
                    
                    for result in data.get("results", []):
                        results.append({
                            "url": result.get("urls", {}).get("regular"),
                            "title": result.get("description") or result.get("alt_description") or query,
                            "source": "unsplash.com",
                            "author": result.get("user", {}).get("name")
                        })
                    
                    return results
        except Exception as e:
            logger.error(f"Error in image search: {str(e)}")
            raise MCPError(f"Image search failed: {str(e)}")
    
    async def summarize_text(self, text: str, max_length: int = 200) -> str:
        """
        Summarize text using the LLM.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of the summary
            
        Returns:
            Summarized text
        """
        try:
            # Create a prompt for summarization
            prompt = f"Summarize the following text in {max_length} words or less:\n\n{text}"
            
            # Create a properly formatted message with Role enum
            messages = [{
                "role": Role.USER.value,  # Use the value of the enum
                "content": prompt
            }]
            
            # Send the request directly
            response = await self._send_mcp_request(messages)
            
            # Extract the content from the response
            if response and "choices" in response and len(response["choices"]) > 0:
                return response["choices"][0]["message"]["content"]
            else:
                raise MCPError("Failed to get a valid response from the LLM")
        except Exception as e:
            logger.error(f"Error in text summarization: {str(e)}")
            raise MCPError(f"Text summarization failed: {str(e)}")
