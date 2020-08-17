from dataclasses import dataclass

from recommender.data.recommendation.recommendation import Recommendation
from recommender.data.search_session import SearchSession


@dataclass
class RecommendationResponse:
    search_session: SearchSession
    recommendation: Recommendation
