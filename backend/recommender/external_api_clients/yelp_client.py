from typing import TypeVar

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from recommender.data.business import Business
from recommender.data.location import Location
from recommender.data.price import PriceCategory
from recommender.external_api_clients.search_client import SearchClient

BUSINESS_SEARCH_QUERY = gql(
    """query businessSearch($lat: Float, $long: Float) {
    search(latitude: $lat,
            longitude: $long,
            limit: 50) {
        total
        business {
            id,
            name
            url,
            rating,
            price
        }
    }
}"""
)

T = TypeVar("T")


class YelpClient(SearchClient):
    @staticmethod
    def array_to_search_string(values_array: [T]) -> str:
        return ", ".join([str(value) for value in values_array])

    def __init__(self, api_key: str) -> None:
        yelp_graph_api_transport = RequestsHTTPTransport(
            url="https://api.yelp.com/v3/graphql",
            use_json=True,
            headers={"Content-type": "application/json", "Authorization": api_key},
            verify=True,
        )
        self.yelp_graph_api_client = Client(
            transport=yelp_graph_api_transport, fetch_schema_from_transport=False
        )

    def business_search(
        self,
        location: Location,
        search_term: str,
        price_categories: [PriceCategory],
        categories: [str],
        attributes: [str],
        radius: int,
    ) -> [Business]:
        lat, long = location
        price_categories_filter = YelpClient.array_to_search_string(
            [
                priceCategory.get_yelp_api_filter_value()
                for priceCategory in price_categories
            ]
        )
        category_filter = YelpClient.array_to_search_string(categories)
        attributes_filter = YelpClient.array_to_search_string(attributes)
        result = self.yelp_graph_api_client.execute(
            BUSINESS_SEARCH_QUERY, {"lat": lat, "long": long}
        )
        search_result = result["search"]
        return [
            Business.from_dict(yelp_dict) for yelp_dict in search_result["business"]
        ]
