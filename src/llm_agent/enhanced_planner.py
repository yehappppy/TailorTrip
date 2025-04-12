"""
Enhanced travel planner agent that uses the MCP toolbox and tools.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import asyncio
from dotenv import load_dotenv

from src.tool_box.mcp_toolbox import MCPConfig, Role
from src.tool_box.travel_tools import TravelTools
from src.prompt.travel_planner import TRAVEL_PLANNER_SYSTEM_PROMPT, create_user_prompt

# Load environment variables
load_dotenv('./config/.env')

logger = logging.getLogger(__name__)

class EnhancedTravelPlannerAgent:
    """
    Enhanced travel planner agent that uses the MCP toolbox and tools.
    """
    
    def __init__(self):
        """Initialize the enhanced travel planner agent."""
        # Configure the MCP toolbox
        self.mcp_config = MCPConfig(
            model_endpoint=os.getenv('LLM_BASE_URL', 'https://api.openai.com/v1'),
            protocol_version="mcp-v1.0",
            context_window=int(os.getenv('LLM_MAX_TOKENS', '8192')),
            default_headers={
                "Authorization": f"Bearer {os.getenv('LLM_API_KEY')}"
            },
            timeout=30,
            max_retries=3
        )
        
        # Initialize the travel tools
        self.travel_tools = TravelTools(self.mcp_config)
        
        # Set up logging and results directories
        self.log_dir = os.path.join(os.getcwd(), os.getenv('LOG_DIR', 'data/logs'))
        self.results_dir = os.path.join(os.getcwd(), os.getenv('RESULTS_DIR', 'data/results'))
        
        # Create directories if they don't exist
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Define available tools
        self.available_tools = [
            {
                "name": "attraction_search",
                "description": "Search for attractions in a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "Location to search in"},
                        "category": {"type": "string", "description": "Optional category (e.g., 'museum', 'park', 'historical')"},
                        "limit": {"type": "integer", "description": "Maximum number of results to return"}
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "hotel_search",
                "description": "Search for hotels in a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "Location to search in"},
                        "check_in": {"type": "string", "description": "Check-in date (YYYY-MM-DD)"},
                        "check_out": {"type": "string", "description": "Check-out date (YYYY-MM-DD)"},
                        "guests": {"type": "integer", "description": "Number of guests"},
                        "price_range": {"type": "string", "description": "Optional price range (e.g., 'budget', 'mid-range', 'luxury')"}
                    },
                    "required": ["location", "check_in", "check_out"]
                }
            },
            {
                "name": "restaurant_search",
                "description": "Search for restaurants in a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "Location to search in"},
                        "cuisine": {"type": "string", "description": "Optional cuisine type"},
                        "price_range": {"type": "string", "description": "Optional price range (e.g., '$', '$$', '$$$')"},
                        "limit": {"type": "integer", "description": "Maximum number of results to return"}
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "weather_info",
                "description": "Get weather information for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "Location to get weather for"}
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "travel_advisory",
                "description": "Get travel advisory information for a country",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "country": {"type": "string", "description": "Country to get advisory for"}
                    },
                    "required": ["country"]
                }
            },
            {
                "name": "local_events",
                "description": "Get local events in a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "Location to search in"},
                        "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                        "end_date": {"type": "string", "description": "Optional end date (YYYY-MM-DD)"},
                        "category": {"type": "string", "description": "Optional category (e.g., 'music', 'sports', 'cultural')"},
                        "limit": {"type": "integer", "description": "Maximum number of results to return"}
                    },
                    "required": ["location", "start_date"]
                }
            }
        ]
    
    async def generate_enhanced_itinerary(self, user_profile: Dict[str, Any], destination: str) -> Dict[str, Any]:
        """
        Generate an enhanced travel itinerary based on user profile and destination.
        Uses tools to gather information and create a more detailed itinerary.
        
        Args:
            user_profile: User profile with preferences
            destination: Destination for the itinerary
            
        Returns:
            Enhanced itinerary with additional information
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        request_id = f"{destination.replace(' ', '_')}_{timestamp}"
        
        # Log the request
        self._log_request(request_id, user_profile, destination)
        
        try:
            # Create the system prompt
            system_message = {
                "role": Role.SYSTEM,
                "content": TRAVEL_PLANNER_SYSTEM_PROMPT + "\n\nYou have access to tools to gather information about the destination. Use these tools to create a more detailed and personalized itinerary."
            }
            
            # Create the user prompt
            user_prompt = create_user_prompt(user_profile, destination)
            user_message = {
                "role": Role.USER,
                "content": user_prompt
            }
            
            # Set up the context
            context = [system_message, user_message]
            
            # Use tool-enhanced query to generate the itinerary
            response = await self.travel_tools.tool_enhanced_query(
                query=user_prompt,
                available_tools=self.available_tools,
                max_tool_calls=5
            )
            
            # Format and save the response
            if isinstance(response, str):
                itinerary = self._format_response(response)
                self._save_result(request_id, itinerary)
                
                logger.info(f"Successfully generated enhanced itinerary for {destination}")
                return itinerary
            else:
                # Handle error case
                error_msg = f"Error generating itinerary: {response.get('error', 'Unknown error')}"
                logger.error(error_msg)
                self._log_error(request_id, error_msg)
                return f"Error: {error_msg}"
            
        except Exception as e:
            error_msg = f"Error generating enhanced itinerary: {str(e)}"
            logger.error(error_msg)
            self._log_error(request_id, error_msg)
            return f"Error: {str(e)}"
    
    def _log_request(self, request_id: str, user_profile: Dict[str, Any], destination: str):
        """Log the user request."""
        log_file = os.path.join(self.log_dir, f"{request_id}_request.json")
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "user_profile": user_profile,
            "destination": destination
        }
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2)

    def _save_result(self, request_id: str, itinerary: str):
        """Save the generated itinerary."""
        result_file = os.path.join(self.results_dir, f"{request_id}_result.md")
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write(itinerary)

    def _log_error(self, request_id: str, error_msg: str):
        """Log any errors that occur."""
        error_file = os.path.join(self.log_dir, f"{request_id}_error.log")
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()}: {error_msg}")

    def _format_response(self, response: str) -> str:
        """Clean and format the response from LLM."""
        # Remove markdown code block if present
        response = response.strip()
        if response.startswith('```markdown'):
            response = response[len('```markdown'):].strip()
        if response.endswith('```'):
            response = response[:-3].strip()
        return response
