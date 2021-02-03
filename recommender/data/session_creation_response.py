from dataclasses import dataclass

from recommender.data.recommendation.displayable_recommendation import (
    DisplayableRecommendation,
)
from recommender.data.serializable import serializable_persistence_object


@serializable_persistence_object
@dataclass
class SessionCreationResponse:
    session_id: str
    recommendation: DisplayableRecommendation
