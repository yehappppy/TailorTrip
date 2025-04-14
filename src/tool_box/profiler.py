from pydantic import BaseModel
from typing import List, Optional
from sklearn.cluster import KMeans
import logging

logger = logging.getLogger(__name__)

class TravelPreferences(BaseModel):
    budget_level: str  # low, mid, high
    travel_style: List[str]  # adventure, cultural, relaxation, etc.
    accessibility_needs: List[str]
    interests: List[str]

class UserProfile(BaseModel):
    explicit_prefs: TravelPreferences
    implicit_features: dict
    behavioral_cluster: Optional[int] = None

class UserProfiler:
    def __init__(self):
        self.cluster_model = KMeans(n_clusters=5)
        self.is_trained = False

    def create_profile(self, questionnaire: dict, behavior_data: dict) -> UserProfile:
        # Process explicit preferences
        explicit_prefs = TravelPreferences(**questionnaire)
        
        # Analyze implicit behavior
        features = self._extract_features(behavior_data)
        
        # Cluster users
        if self.is_trained:
            cluster = self.cluster_model.predict([features])[0]
        else:
            cluster = -1
        
        return UserProfile(
            explicit_prefs=explicit_prefs,
            implicit_features=features,
            behavioral_cluster=cluster
        )

    def _extract_features(self, behavior_data: dict) -> dict:
        # Feature engineering from behavior data
        return {
            'activity_pace': behavior_data.get('avg_daily_activities', 3),
            'preferred_time': behavior_data.get('preferred_wakeup', 8),
            'social_ratio': behavior_data.get('social_interactions', 0.5)
        }
