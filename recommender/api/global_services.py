import os

from recommender.api.utils.auth_route_utils import AuthRouteUtils
from recommender.business.business_manager import BusinessManager
from recommender.business.yelp_client import YelpClient
from recommender.data.user.user_manager import UserManager

api_key = os.environ["YELP_API_KEY"]
__yelp_client: YelpClient = YelpClient(api_key)
user_manager = UserManager()
auth_route_utils = AuthRouteUtils(user_manager)
business_manager: BusinessManager = BusinessManager(__yelp_client)
