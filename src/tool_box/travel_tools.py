"""
Travel-specific tools implementation for TailorTrip.
These tools extend the MCPToolbox to provide travel-related functionality.
"""

import json
import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging
import aiohttp
import asyncio
import re

from src.tool_box.mcp_toolbox import MCPToolbox, MCPConfig, MCPError, Role
from src.tool_box.general_tools import GeneralTools

logger = logging.getLogger(__name__)

class TravelTools(GeneralTools):
    """
    Implementation of travel-specific tools extending the GeneralTools.
    """
    
    def __init__(self, config: MCPConfig):
        """Initialize with MCPConfig."""
        super().__init__(config)
    
    async def _execute_single_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        Execute a single tool with proper validation and execution.
        
        Args:
            tool_name: Name of the tool to execute
            args: Arguments for the tool
            
        Returns:
            Result of the tool execution
        """
        travel_tool_mapping = {
            "attraction_search": self.attraction_search,
            "hotel_search": self.hotel_search,
            "flight_search": self.flight_search,
            "restaurant_search": self.restaurant_search,
            "travel_advisory": self.travel_advisory,
            "local_events": self.local_events,
            "distance_calculator": self.distance_calculator,
            "language_translator": self.language_translator
        }
        
        if tool_name in travel_tool_mapping:
            return await travel_tool_mapping[tool_name](**args)
        
        # If not a travel-specific tool, try the general tools
        return await super()._execute_single_tool(tool_name, args)
    
    async def attraction_search(self, location: str, category: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for attractions in a location.
        
        Args:
            location: Location to search in
            category: Optional category (e.g., "museum", "park", "historical")
            limit: Maximum number of results to return
            
        Returns:
            List of attractions with details
        """
        try:
            # In a production environment, you would use a real API like Google Places
            # This is a simplified implementation for demonstration
            
            # Mock data for demonstration
            attractions = {
                "tokyo": [
                    {"name": "Tokyo Skytree", "category": "landmark", "rating": 4.5, "description": "Tallest structure in Japan with observation decks."},
                    {"name": "Senso-ji Temple", "category": "historical", "rating": 4.7, "description": "Ancient Buddhist temple in Asakusa."},
                    {"name": "Meiji Shrine", "category": "historical", "rating": 4.6, "description": "Shinto shrine dedicated to Emperor Meiji."},
                    {"name": "Tokyo Disneyland", "category": "amusement", "rating": 4.8, "description": "Disney theme park in Tokyo."},
                    {"name": "Ueno Park", "category": "park", "rating": 4.4, "description": "Large public park with museums and zoo."},
                    {"name": "Shibuya Crossing", "category": "landmark", "rating": 4.5, "description": "Famous busy intersection in Tokyo."},
                    {"name": "Tokyo National Museum", "category": "museum", "rating": 4.6, "description": "Japan's oldest and largest museum."}
                ],
                "paris": [
                    {"name": "Eiffel Tower", "category": "landmark", "rating": 4.7, "description": "Iconic iron tower on the Champ de Mars."},
                    {"name": "Louvre Museum", "category": "museum", "rating": 4.8, "description": "World's largest art museum and historic monument."},
                    {"name": "Notre-Dame Cathedral", "category": "historical", "rating": 4.7, "description": "Medieval Catholic cathedral on the Île de la Cité."},
                    {"name": "Arc de Triomphe", "category": "landmark", "rating": 4.6, "description": "Iconic triumphal arch honoring those who fought for France."},
                    {"name": "Montmartre", "category": "district", "rating": 4.5, "description": "Large hill in Paris's 18th arrondissement with artistic history."},
                    {"name": "Champs-Élysées", "category": "shopping", "rating": 4.4, "description": "Famous avenue known for luxury shops and cafes."}
                ]
            }
            
            # Normalize location for lookup
            location_key = location.lower().replace(" ", "")
            
            # Get attractions for the location
            location_attractions = attractions.get(location_key, [])
            
            # Filter by category if provided
            if category:
                location_attractions = [a for a in location_attractions if a["category"].lower() == category.lower()]
            
            # Add location and timestamp to each attraction
            for attraction in location_attractions:
                attraction["location"] = location
                attraction["timestamp"] = datetime.utcnow().isoformat()
            
            return location_attractions[:limit]
            
        except Exception as e:
            logger.error(f"Error in attraction search: {str(e)}")
            raise MCPError(f"Attraction search failed: {str(e)}")
    
    async def hotel_search(self, location: str, check_in: str, check_out: str, guests: int = 2, 
                          price_range: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for hotels in a location.
        
        Args:
            location: Location to search in
            check_in: Check-in date (YYYY-MM-DD)
            check_out: Check-out date (YYYY-MM-DD)
            guests: Number of guests
            price_range: Optional price range (e.g., "budget", "mid-range", "luxury")
            
        Returns:
            List of hotels with details
        """
        try:
            # Mock data for demonstration
            hotels = {
                "tokyo": [
                    {"name": "Park Hyatt Tokyo", "rating": 4.8, "price_category": "luxury", "price_per_night": 450, 
                     "amenities": ["spa", "pool", "restaurant", "fitness center"]},
                    {"name": "Hotel Gracery Shinjuku", "rating": 4.5, "price_category": "mid-range", "price_per_night": 200, 
                     "amenities": ["restaurant", "free wifi"]},
                    {"name": "Sakura Hotel Ikebukuro", "rating": 4.0, "price_category": "budget", "price_per_night": 80, 
                     "amenities": ["free wifi", "shared kitchen"]},
                    {"name": "Conrad Tokyo", "rating": 4.7, "price_category": "luxury", "price_per_night": 400, 
                     "amenities": ["spa", "pool", "restaurant", "fitness center"]},
                    {"name": "Shinjuku Washington Hotel", "rating": 4.2, "price_category": "mid-range", "price_per_night": 150, 
                     "amenities": ["restaurant", "free wifi"]}
                ],
                "paris": [
                    {"name": "Ritz Paris", "rating": 4.9, "price_category": "luxury", "price_per_night": 1000, 
                     "amenities": ["spa", "pool", "restaurant", "fitness center"]},
                    {"name": "Hôtel Mercure Paris Centre", "rating": 4.3, "price_category": "mid-range", "price_per_night": 180, 
                     "amenities": ["restaurant", "free wifi"]},
                    {"name": "Generator Paris", "rating": 4.1, "price_category": "budget", "price_per_night": 70, 
                     "amenities": ["free wifi", "bar"]},
                    {"name": "Four Seasons Hotel George V", "rating": 4.8, "price_category": "luxury", "price_per_night": 950, 
                     "amenities": ["spa", "pool", "restaurant", "fitness center"]},
                    {"name": "Ibis Paris Eiffel Tower", "rating": 4.0, "price_category": "mid-range", "price_per_night": 120, 
                     "amenities": ["restaurant", "free wifi"]}
                ]
            }
            
            # Normalize location for lookup
            location_key = location.lower().replace(" ", "")
            
            # Get hotels for the location
            location_hotels = hotels.get(location_key, [])
            
            # Filter by price range if provided
            if price_range:
                location_hotels = [h for h in location_hotels if h["price_category"].lower() == price_range.lower()]
            
            # Add booking details to each hotel
            for hotel in location_hotels:
                hotel["location"] = location
                hotel["check_in"] = check_in
                hotel["check_out"] = check_out
                hotel["guests"] = guests
                hotel["timestamp"] = datetime.utcnow().isoformat()
            
            return location_hotels
            
        except Exception as e:
            logger.error(f"Error in hotel search: {str(e)}")
            raise MCPError(f"Hotel search failed: {str(e)}")
    
    async def flight_search(self, origin: str, destination: str, date: str, 
                           return_date: Optional[str] = None, passengers: int = 1) -> List[Dict[str, Any]]:
        """
        Search for flights between two locations.
        
        Args:
            origin: Origin location (airport code or city)
            destination: Destination location (airport code or city)
            date: Departure date (YYYY-MM-DD)
            return_date: Optional return date for round trips
            passengers: Number of passengers
            
        Returns:
            List of flights with details
        """
        try:
            # Mock data for demonstration
            flight_routes = {
                "tokyo-paris": [
                    {"airline": "Air France", "flight_number": "AF273", "departure_time": "10:30", "arrival_time": "16:45", 
                     "duration": "12h 15m", "price": 950, "stops": 0},
                    {"airline": "JAL", "flight_number": "JL416", "departure_time": "12:15", "arrival_time": "18:30", 
                     "duration": "12h 15m", "price": 1050, "stops": 0},
                    {"airline": "Lufthansa", "flight_number": "LH797", "departure_time": "14:00", "arrival_time": "22:30", 
                     "duration": "14h 30m", "price": 850, "stops": 1}
                ],
                "paris-tokyo": [
                    {"airline": "Air France", "flight_number": "AF272", "departure_time": "13:30", "arrival_time": "09:45", 
                     "duration": "12h 15m", "price": 980, "stops": 0},
                    {"airline": "JAL", "flight_number": "JL415", "departure_time": "11:45", "arrival_time": "08:00", 
                     "duration": "12h 15m", "price": 1100, "stops": 0},
                    {"airline": "KLM", "flight_number": "KL862", "departure_time": "09:30", "arrival_time": "06:45", 
                     "duration": "13h 15m", "price": 890, "stops": 1}
                ]
            }
            
            # Normalize route for lookup
            route_key = f"{origin.lower().replace(' ', '')}-{destination.lower().replace(' ', '')}"
            
            # Get flights for the route
            route_flights = flight_routes.get(route_key, [])
            
            # Add booking details to each flight
            for flight in route_flights:
                flight["origin"] = origin
                flight["destination"] = destination
                flight["date"] = date
                flight["return_date"] = return_date
                flight["passengers"] = passengers
                flight["total_price"] = flight["price"] * passengers
                flight["timestamp"] = datetime.utcnow().isoformat()
            
            # If return date is provided, include return flights
            if return_date:
                return_route_key = f"{destination.lower().replace(' ', '')}-{origin.lower().replace(' ', '')}"
                return_flights = flight_routes.get(return_route_key, [])
                
                for flight in return_flights:
                    flight["origin"] = destination
                    flight["destination"] = origin
                    flight["date"] = return_date
                    flight["passengers"] = passengers
                    flight["total_price"] = flight["price"] * passengers
                    flight["timestamp"] = datetime.utcnow().isoformat()
                
                # Combine outbound and return flights
                combined_flights = []
                for outbound in route_flights:
                    for inbound in return_flights:
                        combined_flights.append({
                            "outbound": outbound,
                            "inbound": inbound,
                            "total_price": outbound["total_price"] + inbound["total_price"],
                            "timestamp": datetime.utcnow().isoformat()
                        })
                
                return combined_flights
            
            return route_flights
            
        except Exception as e:
            logger.error(f"Error in flight search: {str(e)}")
            raise MCPError(f"Flight search failed: {str(e)}")
    
    async def restaurant_search(self, location: str, cuisine: Optional[str] = None, 
                              price_range: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for restaurants in a location.
        
        Args:
            location: Location to search in
            cuisine: Optional cuisine type
            price_range: Optional price range (e.g., "$", "$$", "$$$")
            limit: Maximum number of results to return
            
        Returns:
            List of restaurants with details
        """
        try:
            # Mock data for demonstration
            restaurants = {
                "tokyo": [
                    {"name": "Sukiyabashi Jiro", "cuisine": "sushi", "price_range": "$$$", "rating": 4.9, 
                     "address": "Chuo City, Ginza, 4-2-15"},
                    {"name": "Ichiran Ramen", "cuisine": "ramen", "price_range": "$$", "rating": 4.7, 
                     "address": "1 Chome-22-7 Jinnan, Shibuya City"},
                    {"name": "Gonpachi", "cuisine": "izakaya", "price_range": "$$", "rating": 4.5, 
                     "address": "1-13-11 Nishi-Azabu, Minato City"},
                    {"name": "Tempura Kondo", "cuisine": "tempura", "price_range": "$$$", "rating": 4.8, 
                     "address": "9F, 5-5-13 Ginza, Chuo-ku"},
                    {"name": "Yoshinoya", "cuisine": "donburi", "price_range": "$", "rating": 4.0, 
                     "address": "Various locations throughout Tokyo"}
                ],
                "paris": [
                    {"name": "Le Jules Verne", "cuisine": "french", "price_range": "$$$", "rating": 4.7, 
                     "address": "Eiffel Tower, 2nd floor, Champ de Mars"},
                    {"name": "Chez L'Ami Jean", "cuisine": "french", "price_range": "$$", "rating": 4.8, 
                     "address": "27 Rue Malar, 75007"},
                    {"name": "L'As du Fallafel", "cuisine": "middle eastern", "price_range": "$", "rating": 4.6, 
                     "address": "34 Rue des Rosiers, 75004"},
                    {"name": "Septime", "cuisine": "contemporary", "price_range": "$$$", "rating": 4.9, 
                     "address": "80 Rue de Charonne, 75011"},
                    {"name": "Bouillon Chartier", "cuisine": "french", "price_range": "$", "rating": 4.3, 
                     "address": "7 Rue du Faubourg Montmartre, 75009"}
                ]
            }
            
            # Normalize location for lookup
            location_key = location.lower().replace(" ", "")
            
            # Get restaurants for the location
            location_restaurants = restaurants.get(location_key, [])
            
            # Filter by cuisine if provided
            if cuisine:
                location_restaurants = [r for r in location_restaurants if r["cuisine"].lower() == cuisine.lower()]
            
            # Filter by price range if provided
            if price_range:
                location_restaurants = [r for r in location_restaurants if r["price_range"] == price_range]
            
            # Add location and timestamp to each restaurant
            for restaurant in location_restaurants:
                restaurant["location"] = location
                restaurant["timestamp"] = datetime.utcnow().isoformat()
            
            return location_restaurants[:limit]
            
        except Exception as e:
            logger.error(f"Error in restaurant search: {str(e)}")
            raise MCPError(f"Restaurant search failed: {str(e)}")
    
    async def travel_advisory(self, country: str) -> Dict[str, Any]:
        """
        Get travel advisory information for a country.
        
        Args:
            country: Country to get advisory for
            
        Returns:
            Travel advisory information
        """
        try:
            # Mock data for demonstration
            advisories = {
                "japan": {
                    "advisory_level": "Level 1: Exercise Normal Precautions",
                    "last_updated": "2025-03-15",
                    "summary": "Exercise normal precautions in Japan.",
                    "safety_info": [
                        "Japan has a low crime rate, but petty crime does occur.",
                        "Natural disasters such as earthquakes, tsunamis, and typhoons can occur.",
                        "Medical care is widely available and of high quality."
                    ],
                    "entry_requirements": [
                        "Valid passport required",
                        "Visa not required for stays under 90 days for tourism"
                    ]
                },
                "france": {
                    "advisory_level": "Level 2: Exercise Increased Caution",
                    "last_updated": "2025-03-10",
                    "summary": "Exercise increased caution in France due to terrorism and civil unrest.",
                    "safety_info": [
                        "Terrorist groups continue plotting possible attacks in France.",
                        "Demonstrations in Paris and other cities may turn violent.",
                        "Petty crime, especially pickpocketing, is common in tourist areas."
                    ],
                    "entry_requirements": [
                        "Valid passport required",
                        "Visa not required for stays under 90 days for tourism"
                    ]
                }
            }
            
            # Normalize country for lookup
            country_key = country.lower().replace(" ", "")
            
            # Get advisory for the country
            country_advisory = advisories.get(country_key, {
                "advisory_level": "Information not available",
                "last_updated": datetime.utcnow().strftime("%Y-%m-%d"),
                "summary": f"Travel advisory information for {country} is not available.",
                "safety_info": [],
                "entry_requirements": []
            })
            
            # Add country and timestamp
            country_advisory["country"] = country
            country_advisory["timestamp"] = datetime.utcnow().isoformat()
            
            return country_advisory
            
        except Exception as e:
            logger.error(f"Error in travel advisory: {str(e)}")
            raise MCPError(f"Travel advisory failed: {str(e)}")
    
    async def local_events(self, location: str, start_date: str, end_date: Optional[str] = None, 
                         category: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get local events in a location.
        
        Args:
            location: Location to search in
            start_date: Start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            category: Optional category (e.g., "music", "sports", "cultural")
            limit: Maximum number of results to return
            
        Returns:
            List of events with details
        """
        try:
            # Mock data for demonstration
            events = {
                "tokyo": [
                    {"name": "Tokyo Summer Festival", "category": "cultural", "date": "2025-07-15", 
                     "venue": "Yoyogi Park", "description": "Annual summer festival with food stalls and performances."},
                    {"name": "J-League Soccer Match", "category": "sports", "date": "2025-06-20", 
                     "venue": "Tokyo Stadium", "description": "Professional soccer match in Japan's top league."},
                    {"name": "Anime Japan Expo", "category": "entertainment", "date": "2025-06-25", 
                     "venue": "Tokyo Big Sight", "description": "Large anime and manga convention."},
                    {"name": "Summer Sonic Music Festival", "category": "music", "date": "2025-08-10", 
                     "venue": "Makuhari Messe", "description": "Major music festival featuring international artists."},
                    {"name": "Traditional Tea Ceremony", "category": "cultural", "date": "2025-07-05", 
                     "venue": "Happo-en Garden", "description": "Experience traditional Japanese tea ceremony."}
                ],
                "paris": [
                    {"name": "Bastille Day Celebrations", "category": "cultural", "date": "2025-07-14", 
                     "venue": "Eiffel Tower", "description": "National holiday with fireworks and parades."},
                    {"name": "Roland Garros Tennis Tournament", "category": "sports", "date": "2025-05-25", 
                     "venue": "Stade Roland Garros", "description": "Major international tennis tournament."},
                    {"name": "Paris Fashion Week", "category": "fashion", "date": "2025-09-28", 
                     "venue": "Various venues", "description": "International fashion event showcasing new collections."},
                    {"name": "Jazz Festival", "category": "music", "date": "2025-06-15", 
                     "venue": "Parc Floral", "description": "Annual jazz music festival in Paris."},
                    {"name": "Nuit des Musées", "category": "cultural", "date": "2025-05-18", 
                     "venue": "Various museums", "description": "Night when museums stay open late with special events."}
                ]
            }
            
            # Normalize location for lookup
            location_key = location.lower().replace(" ", "")
            
            # Get events for the location
            location_events = events.get(location_key, [])
            
            # Filter by date range
            filtered_events = []
            for event in location_events:
                event_date = datetime.strptime(event["date"], "%Y-%m-%d")
                start = datetime.strptime(start_date, "%Y-%m-%d")
                
                if end_date:
                    end = datetime.strptime(end_date, "%Y-%m-%d")
                    if start <= event_date <= end:
                        filtered_events.append(event)
                else:
                    if event_date >= start:
                        filtered_events.append(event)
            
            # Filter by category if provided
            if category:
                filtered_events = [e for e in filtered_events if e["category"].lower() == category.lower()]
            
            # Add location and timestamp to each event
            for event in filtered_events:
                event["location"] = location
                event["timestamp"] = datetime.utcnow().isoformat()
            
            return filtered_events[:limit]
            
        except Exception as e:
            logger.error(f"Error in local events: {str(e)}")
            raise MCPError(f"Local events search failed: {str(e)}")
    
    async def distance_calculator(self, origin: str, destination: str, mode: str = "driving") -> Dict[str, Any]:
        """
        Calculate distance and travel time between two locations.
        
        Args:
            origin: Origin location
            destination: Destination location
            mode: Travel mode (driving, walking, transit, cycling)
            
        Returns:
            Distance and travel time information
        """
        try:
            # Mock data for demonstration
            distances = {
                "tokyo-kyoto": {
                    "driving": {"distance": "460 km", "duration": "5 hours 30 minutes"},
                    "transit": {"distance": "460 km", "duration": "2 hours 20 minutes", "method": "Shinkansen"},
                    "cycling": {"distance": "460 km", "duration": "23 hours"},
                    "walking": {"distance": "460 km", "duration": "96 hours"}
                },
                "paris-lyon": {
                    "driving": {"distance": "465 km", "duration": "4 hours 30 minutes"},
                    "transit": {"distance": "465 km", "duration": "2 hours", "method": "TGV"},
                    "cycling": {"distance": "465 km", "duration": "24 hours"},
                    "walking": {"distance": "465 km", "duration": "97 hours"}
                }
            }
            
            # Normalize route for lookup
            route_key = f"{origin.lower().replace(' ', '')}-{destination.lower().replace(' ', '')}"
            
            # Check if route exists, otherwise return estimated data
            if route_key in distances:
                route_distances = distances[route_key]
                
                # Get distance for the specified mode
                if mode in route_distances:
                    result = route_distances[mode]
                else:
                    result = route_distances["driving"]  # Default to driving
            else:
                # Generate estimated data
                result = {
                    "distance": "Unknown",
                    "duration": "Unknown",
                    "note": "Estimated data not available for this route"
                }
            
            # Add route and timestamp
            result["origin"] = origin
            result["destination"] = destination
            result["mode"] = mode
            result["timestamp"] = datetime.utcnow().isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"Error in distance calculator: {str(e)}")
            raise MCPError(f"Distance calculation failed: {str(e)}")
    
    async def language_translator(self, text: str, source_language: str, target_language: str) -> Dict[str, str]:
        """
        Translate text between languages.
        
        Args:
            text: Text to translate
            source_language: Source language code (e.g., "en", "ja", "fr")
            target_language: Target language code
            
        Returns:
            Translated text
        """
        try:
            # Mock translations for common phrases
            translations = {
                "en-ja": {
                    "hello": "こんにちは",
                    "thank you": "ありがとう",
                    "excuse me": "すみません",
                    "where is the bathroom": "お手洗いはどこですか",
                    "how much does this cost": "これはいくらですか"
                },
                "en-fr": {
                    "hello": "bonjour",
                    "thank you": "merci",
                    "excuse me": "excusez-moi",
                    "where is the bathroom": "où sont les toilettes",
                    "how much does this cost": "combien ça coûte"
                },
                "ja-en": {
                    "こんにちは": "hello",
                    "ありがとう": "thank you",
                    "すみません": "excuse me",
                    "お手洗いはどこですか": "where is the bathroom",
                    "これはいくらですか": "how much does this cost"
                },
                "fr-en": {
                    "bonjour": "hello",
                    "merci": "thank you",
                    "excusez-moi": "excuse me",
                    "où sont les toilettes": "where is the bathroom",
                    "combien ça coûte": "how much does this cost"
                }
            }
            
            # Normalize language pair for lookup
            lang_pair = f"{source_language.lower()}-{target_language.lower()}"
            
            # Check if language pair exists
            if lang_pair in translations:
                # Check if the exact text exists in the dictionary
                if text.lower() in translations[lang_pair]:
                    translated_text = translations[lang_pair][text.lower()]
                else:
                    # For demonstration, return a message about translation
                    translated_text = f"[Translation from {source_language} to {target_language}]: {text}"
            else:
                translated_text = f"[Translation from {source_language} to {target_language} not available]: {text}"
            
            return {
                "original_text": text,
                "translated_text": translated_text,
                "source_language": source_language,
                "target_language": target_language,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in language translator: {str(e)}")
            raise MCPError(f"Translation failed: {str(e)}")
