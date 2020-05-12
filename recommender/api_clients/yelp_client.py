import os
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from recommender.data.location import Location

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
            rating
        }
    }
}"""
)


class YelpClient:
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

    def businesses_search(self, location: Location):
        lat, long = location
        return self.yelp_graph_api_client.execute(
            BUSINESS_SEARCH_QUERY, {"lat": lat, "long": long}
        )
