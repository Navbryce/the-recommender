from dataclasses import dataclass

from recommender.data.business import Business
from recommender.data.search_session import SearchSession

@dataclass
class RecommendationResponse:
    search_session: SearchSession
    recommendation: Business
