import os

from recommender.business.business_manager import BusinessManager
from recommender.business.yelp_client import YelpClient

api_key = os.environ["YELP_API_KEY"]
__yelp_client: YelpClient = YelpClient(api_key)
business_manager: BusinessManager = BusinessManager(__yelp_client)
