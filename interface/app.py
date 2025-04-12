import streamlit as st
import logging
import asyncio
from typing import Optional, Union
from llm_agent.planner import TravelPlannerAgent
from llm_agent.enhanced_planner import EnhancedTravelPlannerAgent

logger = logging.getLogger(__name__)

def render_markdown_sections(markdown_text: str) -> None:
    """
    Renders markdown content in a more visually appealing way with proper HTML structure.
    """
    st.markdown("""
        <style>
        .itinerary-container {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        .itinerary-container h1 {
            color: #1e88e5;
            font-size: 2.2rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e3f2fd;
        }
        .itinerary-container h2 {
            color: #2196f3;
            font-size: 1.8rem;
            font-weight: 500;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        .itinerary-container h3 {
            color: #1976d2;
            font-size: 1.4rem;
            font-weight: 500;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }
        .itinerary-container p {
            color: #424242;
            font-size: 1rem;
            line-height: 1.6;
            margin-bottom: 1rem;
        }
        .itinerary-container ul, .itinerary-container ol {
            color: #424242;
            margin: 1rem 0 1rem 1.5rem;
            padding-left: 1rem;
        }
        .itinerary-container li {
            margin-bottom: 0.5rem;
            line-height: 1.5;
        }
        .itinerary-container strong {
            color: #1565c0;
        }
        .itinerary-container em {
            color: #0d47a1;
        }
        .itinerary-container hr {
            margin: 2rem 0;
            border: none;
            border-top: 1px solid #e0e0e0;
        }
        .itinerary-container blockquote {
            margin: 1rem 0;
            padding-left: 1rem;
            border-left: 4px solid #90caf9;
            color: #616161;
        }
        </style>
    """, unsafe_allow_html=True)

    # Wrap the markdown content in the styled container
    st.markdown(f"""
        <div class="itinerary-container">
            {markdown_text}
        </div>
    """, unsafe_allow_html=True)

def main(planner: Optional[Union[TravelPlannerAgent, EnhancedTravelPlannerAgent]] = None):
    st.set_page_config(
        page_title="TailorTrip - AI Travel Planner",
        page_icon="✈️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stButton>button {
            width: 100%;
        }
        .stAlert {
            padding: 1rem;
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Title and description
    st.title("✈️ TailorTrip")
    st.markdown("*Your AI-powered travel companion*")
    
    # Create two columns for the layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 🎯 Trip Preferences")
        
        # Input form
        with st.form("trip_form"):
            destination = st.text_input("Where do you want to go? 🌍", 
                                     placeholder="e.g., Tokyo, Paris, New York")
            
            budget = st.select_slider("Budget Level 💰",
                                    options=["Low", "Mid", "High"],
                                    value="Mid")
            
            styles = st.multiselect("Travel Style 🎨",
                                  ["Adventure", "Cultural", "Relaxation", 
                                   "Shopping", "Nature", "Food", "Photography"],
                                  default=["Cultural"])
            
            duration = st.slider("Trip Duration (Days) 📅", 
                               min_value=1, max_value=14, value=7)
            
            submitted = st.form_submit_button("Plan My Trip 🚀")
    
    # Main content area
    with col2:
        if submitted:
            if not destination:
                st.error("Please enter a destination")
                return
                
            if not planner:
                st.error("Travel planner system is not initialized")
                return
                
            try:
                with st.spinner("🎨 Crafting your perfect itinerary..."):
                    # Prepare user profile
                    profile = {
                        "budget": budget,
                        "travel_style": styles,
                        "trip_duration": f"{duration}-day"
                    }
                    
                    # Generate itinerary
                    if isinstance(planner, EnhancedTravelPlannerAgent):
                        # Use the enhanced planner with async
                        result = asyncio.run(planner.generate_enhanced_itinerary(profile, destination))
                    else:
                        # Use the regular planner
                        result = planner.generate_itinerary(profile, destination)
                    
                    if isinstance(result, str) and result.startswith("Error:"):
                        st.error(result)
                    else:
                        st.success("✨ Your personalized itinerary is ready!")
                        
                        # Display the rendered markdown content
                        render_markdown_sections(result)
                        
                        # Add download button for the raw markdown
                        st.download_button(
                            label="📥 Download Itinerary",
                            data=result,
                            file_name=f"{destination.lower().replace(' ', '_')}_itinerary.md",
                            mime="text/markdown",
                            help="Download the itinerary in markdown format"
                        )
                    
            except Exception as e:
                logger.error(f"Error while generating itinerary: {str(e)}")
                st.error("An unexpected error occurred. Please try again.")
        else:
            # Show welcome message when no itinerary is generated
            st.markdown("""
            ### 👋 Welcome to TailorTrip!
            
            1. Enter your destination
            2. Adjust your preferences
            3. Click "Plan My Trip"
            
            We'll create a personalized travel itinerary just for you!
            """)

def start_app():
    try:
        # Initialize the enhanced planner
        enhanced_planner = EnhancedTravelPlannerAgent()
        
        # Use the enhanced planner by default
        main(planner=enhanced_planner)
    except Exception as e:
        logger.error(f"Error in Streamlit app: {str(e)}")
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    start_app()
