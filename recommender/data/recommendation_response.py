from dataclasses import dataclass

from recommender.data.business import Business
from recommender.data.search_session import SearchSession

@dataclass
class RecommendationResponse:
    searchSession: SearchSession
    recommendation: Business;