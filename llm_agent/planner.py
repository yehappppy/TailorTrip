import os
import json
from datetime import datetime
from typing import Dict, Any
import logging
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv('./config/.env')

logger = logging.getLogger(__name__)

class TravelPlannerAgent:
    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv('LLM_BASE_URL'),
            api_key=os.getenv('LLM_API_KEY')
        )
        self.model = os.getenv('LLM_MODEL')
        self.max_tokens = int(os.getenv('LLM_MAX_TOKENS', '8192'))
        self.temperature = float(os.getenv('LLM_TEMPERATURE', '0.0'))
        
        # Set up logging and results directories
        self.log_dir = os.path.join(os.getcwd(), os.getenv('LOG_DIR', 'data/logs'))
        self.results_dir = os.path.join(os.getcwd(), os.getenv('RESULTS_DIR', 'data/results'))
        
        # Create directories if they don't exist
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)

    def generate_itinerary(self, user_profile: Dict[str, Any], destination: str) -> Dict[str, Any]:
        """Generate a travel itinerary based on user profile and destination."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        request_id = f"{destination.replace(' ', '_')}_{timestamp}"
        
        # Log the request
        self._log_request(request_id, user_profile, destination)
        
        try:
            # Generate response using the LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a knowledgeable travel planner. Create detailed travel itineraries based on user preferences. Format the response in markdown with clear sections for each day."},
                    {"role": "user", "content": self._create_prompt(user_profile, destination)}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Format and save the response
            itinerary = self._format_response(response.choices[0].message.content)
            self._save_result(request_id, itinerary)
            
            logger.info(f"Successfully generated itinerary for {destination}")
            return itinerary
            
        except Exception as e:
            error_msg = f"Error generating itinerary: {str(e)}"
            logger.error(error_msg)
            self._log_error(request_id, error_msg)
            return f"Error: {str(e)}"

    def _create_prompt(self, user_profile: Dict[str, Any], destination: str) -> str:
        """Create a prompt for the LLM based on user profile and destination."""
        return f"""Please create a detailed travel itinerary for {destination} with the following preferences:
- Budget Level: {user_profile.get('budget', 'Medium')}
- Duration: {user_profile.get('trip_duration', '7-day')}
- Travel Style: {', '.join(user_profile.get('travel_style', ['General']))}

Format the response in markdown with the following sections:
# {destination} Travel Itinerary

## Overview
[Brief overview of the trip]

## Daily Schedule
### Day 1
[Activities for day 1]

### Day 2
[Activities for day 2]
...

## Recommendations
- Restaurants
- Transportation
- Local Tips
- Cultural Considerations

## Budget Breakdown
[Estimated costs for different aspects of the trip]"""

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
