from dataclasses import dataclass

from recommender.data.recommendation.displayable_recommendation import (
    DisplayableRecommendation,
)
from recommender.data.serializable import serializable


@serializable
@dataclass
class SessionCreationResponse:
    session_id: str
    recommendation: DisplayableRecommendation
