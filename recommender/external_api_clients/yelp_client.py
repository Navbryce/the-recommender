import logging
from typing import TypeVar, Final, Dict

import requests
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from recommender.data.recommendation.address import Address
from recommender.data.recommendation.business_search_request import (
    BusinessSearchRequest,
)
from recommender.data.recommendation.displayable_business import DisplayableBusiness
from recommender.data.recommendation.displayable_category import DisplayableCategory
from recommender.data.recommendation.filterable_business import RecommendableBusiness
from recommender.data.recommendation.location import Location
from recommender.data.recommendation.price import PriceCategory
from recommender.external_api_clients.fetch_utils import retry_request
from recommender.external_api_clients.page import Page
from recommender.external_api_clients.search_client import SearchClient

LOGGER = logging.getLogger(__name__)

BUSINESS_SEARCH_QUERY = gql(
    """query businessSearch($lat: Float, $long: Float, $radius: Float, $searchTerm: String, $price: String, $limit: Int, $offset: Int) {
    search(latitude: $lat,
            longitude: $long,
            radius: $radius,
            term: $searchTerm
            price: $price,
            limit: $limit,
            offset: $offset,
            open_now: true) {
        total
        business {
            id,
            name
            url,
            rating,
            price,
            distance
        }
    }
}"""
)

T = TypeVar("T")


class YelpClient(SearchClient):
    @staticmethod
    def array_to_search_string(values_array: [T]) -> str:
        return ", ".join([str(value) for value in values_array])

    BASE_URL: Final[str] = "https://api.yelp.com/v3"

    __headers: Final[Dict[str, str]]
    __yelp_graph_api_client: Client

    def __init__(self, api_key: str) -> None:
        self.__headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        yelp_graph_api_transport = RequestsHTTPTransport(
            url=f"{self.BASE_URL}/graphql",
            use_json=True,
            headers=self.__headers,
            verify=True,
        )

        self.yelp_graph_api_client = Client(
            transport=yelp_graph_api_transport, fetch_schema_from_transport=False
        )

    def business_search(
        self, search_params: BusinessSearchRequest, page: Page
    ) -> [RecommendableBusiness]:
        lat = search_params.location.lat
        long = search_params.location.long

        price_categories_filter = YelpClient.array_to_search_string(
            [
                priceCategory.get_yelp_api_filter_value()
                for priceCategory in search_params.price_categories
            ]
        )
        category_filter = YelpClient.array_to_search_string(search_params.categories)
        attributes_filter = YelpClient.array_to_search_string(search_params.attributes)
        result = self.yelp_graph_api_client.execute(
            BUSINESS_SEARCH_QUERY,
            {
                "term": search_params.search_term,
                "lat": lat,
                "long": long,
                "searchTerm": search_params.search_term,
                "radius": search_params.radius,
                "price": price_categories_filter,
            },
        )
        search_result = result["search"]

        return [
            self.convert_yelp_dict_to_filterable_business(yelp_dict)
            for yelp_dict in search_result["business"]
        ]

    def convert_yelp_dict_to_filterable_business(
        self, yelp_dict: Dict
    ) -> RecommendableBusiness:
        try:
            return RecommendableBusiness.from_dict(yelp_dict)
        except (ValueError, KeyError) as ex:
            LOGGER.debug(yelp_dict)
            raise ex

    def get_displayable_business(self, business_id: str) -> DisplayableBusiness:
        def request_for_business():
            response = requests.get(
                f"{self.BASE_URL}/businesses/{business_id}", headers=self.__headers
            )
            response.raise_for_status()
            try:
                return self.__get_displayable_business_from_yelp_dict(response.json())
            except (ValueError, KeyError) as ex:
                LOGGER.debug(response.json())
                raise ex

        return retry_request(
            request_for_business,
            lambda x: isinstance(x, requests.HTTPError)
            and x.response.status_code >= 500,
            max_retries=5,
            delay=500,
        )

    def __get_displayable_business_from_yelp_dict(
        self, business_dict: Dict
    ) -> DisplayableBusiness:
        displayable_categories = self.__get_displayable_categories(
            business_dict["categories"]
        )

        address = self.__get_address_from_location_dict(business_dict["location"])

        coordinates = business_dict["coordinates"]
        coordinates = Location(
            lat=coordinates["latitude"], long=coordinates["longitude"]
        )

        return DisplayableBusiness(
            id=business_dict["id"],
            name=business_dict["name"],
            url=business_dict["url"],
            image_urls=business_dict["photos"],
            price=PriceCategory.from_api_return_value(business_dict.get("price")),
            rating=business_dict["rating"],
            rating_count=business_dict["review_count"],
            delivery=False,
            pickup=False,
            categories=displayable_categories,
            coordinates=coordinates,
            address=address,
        )

    def __get_address_from_location_dict(self, location_dict: Dict) -> Address:
        combined_address_line = self.__get_combined_address_line(location_dict)
        country = location_dict["country"]
        region = location_dict["state"]
        city = location_dict["city"]
        zip_code = location_dict["zip_code"]

        return Address(
            country=country,
            region=region,
            city=city,
            address_line=combined_address_line,
            zip_code=zip_code,
        )

    def __get_combined_address_line(self, location_dict: Dict) -> str:
        addresses = []
        for address_count in range(1, 4):
            address_value = location_dict[f"address{address_count}"]
            if address_value is None or len(address_value) == 0:
                break
            addresses.append(address_value)
        return ", ".join(addresses)

    def __get_displayable_categories(self, categories: [Dict]) -> [DisplayableCategory]:
        return [
            DisplayableCategory(id=category["alias"], label=category["title"])
            for category in categories
        ]
