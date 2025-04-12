"""
Test script for the TailorTrip tools implementation.
This script tests the basic functionality of the general and travel tools.
"""

import os
import asyncio
import json
from dotenv import load_dotenv
from src.tool_box.mcp_toolbox import MCPConfig, Role
from src.tool_box.general_tools import GeneralTools
from src.tool_box.travel_tools import TravelTools

# Load environment variables
load_dotenv('./config/.env')

async def test_general_tools():
    """Test the general tools functionality."""
    print("\n===== Testing General Tools =====")
    
    # Configure the MCP toolbox
    mcp_config = MCPConfig(
        model_endpoint=os.getenv('LLM_BASE_URL', 'https://api.openai.com/v1'),
        protocol_version="mcp-v1.0",
        context_window=int(os.getenv('LLM_MAX_TOKENS', '8192')),
        default_headers={
            "Authorization": f"Bearer {os.getenv('LLM_API_KEY')}"
        },
        timeout=30,
        max_retries=3
    )
    
    # Initialize the general tools
    general_tools = GeneralTools(mcp_config)
    
    try:
        # Test weather info tool
        print("\nTesting weather_info tool:")
        weather_result = await general_tools.weather_info(location="Tokyo")
        print(json.dumps(weather_result, indent=2))
        
        # Test currency conversion tool
        print("\nTesting currency_convert tool:")
        currency_result = await general_tools.currency_convert(
            amount=100, 
            from_currency="USD", 
            to_currency="JPY"
        )
        print(json.dumps(currency_result, indent=2))
        
        # Test summarize text tool
        print("\nTesting summarize_text tool:")
        summary_result = await general_tools.summarize_text(
            text="Tokyo is the capital and largest city of Japan. It is the political, economic, and cultural center of the country. Tokyo was originally a small fishing village named Edo. The city's name was changed to Tokyo (meaning 'Eastern Capital') when it became the imperial capital in 1868. Today, Tokyo is one of the most populous metropolitan areas in the world, with over 37 million residents in the greater Tokyo area.",
            max_length=50
        )
        print(summary_result)
        
        print("\nGeneral tools tests completed successfully!")
        
    except Exception as e:
        print(f"Error testing general tools: {str(e)}")

async def test_travel_tools():
    """Test the travel tools functionality."""
    print("\n===== Testing Travel Tools =====")
    
    # Configure the MCP toolbox
    mcp_config = MCPConfig(
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
    travel_tools = TravelTools(mcp_config)
    
    try:
        # Test attraction search tool
        print("\nTesting attraction_search tool:")
        attractions_result = await travel_tools.attraction_search(
            location="Tokyo",
            category="historical",
            limit=3
        )
        print(json.dumps(attractions_result, indent=2))
        
        # Test hotel search tool
        print("\nTesting hotel_search tool:")
        hotels_result = await travel_tools.hotel_search(
            location="Tokyo",
            check_in="2025-07-01",
            check_out="2025-07-05",
            guests=2,
            price_range="mid-range"
        )
        print(json.dumps(hotels_result, indent=2))
        
        # Test restaurant search tool
        print("\nTesting restaurant_search tool:")
        restaurants_result = await travel_tools.restaurant_search(
            location="Tokyo",
            cuisine="sushi",
            limit=2
        )
        print(json.dumps(restaurants_result, indent=2))
        
        # Test travel advisory tool
        print("\nTesting travel_advisory tool:")
        advisory_result = await travel_tools.travel_advisory(country="Japan")
        print(json.dumps(advisory_result, indent=2))
        
        print("\nTravel tools tests completed successfully!")
        
    except Exception as e:
        print(f"Error testing travel tools: {str(e)}")

async def main():
    """Main test function."""
    print("Starting TailorTrip tools tests...\n")
    
    # Test general tools
    await test_general_tools()
    
    # Test travel tools
    await test_travel_tools()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
