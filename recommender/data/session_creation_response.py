from dataclasses import dataclass

from recommender.data.recommendation.displayable_recommendation import DisplayableRecommendation


@dataclass
class SessionCreationResponse:
    session_id: str
    recommendation: DisplayableRecommendation
