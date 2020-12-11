from dataclasses import dataclass

from recommender.data.recommendation.displayable_recommendation import (
    DisplayableRecommendation,
)
from recommender.data.serializable import Serializable


@dataclass
class SessionCreationResponse(Serializable):
    session_id: str
    recommendation: DisplayableRecommendation
