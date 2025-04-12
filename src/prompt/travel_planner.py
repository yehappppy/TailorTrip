__author__ = "yh"
__date__ = "2025-04-11"
__description__ = "Travel planner prompt templates"

"""
Travel planner prompt templates.
"""

TRAVEL_PLANNER_SYSTEM_PROMPT = """You are a knowledgeable travel planner. Create detailed travel itineraries based on user preferences. Format the response in markdown with clear sections for each day."""

def create_user_prompt(user_profile, destination):
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
