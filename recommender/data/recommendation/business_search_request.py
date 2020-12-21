from typing import Dict

from sqlalchemy import Column, String, Float, PickleType, ForeignKey
from sqlalchemy.orm import composite

from recommender.data.serializable import serializable
from recommender.data.persistence_object import PersistenceObject
from recommender.db_config import DbBase
from recommender.data.recommendation.location import Location
from recommender.data.recommendation.price import PriceCategory


@serializable
class BusinessSearchRequest(DbBase, PersistenceObject):
    __tablename__ = "search_request"

    @staticmethod
    def from_dict(json_dict: Dict):
        search_term = json_dict.get("searchTerm", "")
        location = Location.from_json(json_dict["location"])
        price_categories = [
            PriceCategory.from_name(category_name)
            for category_name in json_dict.get("priceCategories", [])
        ]
        categories = json_dict.get("categories", [])
        attributes = json_dict.get("attributes", [])
        radius = json_dict["searchRadius"]
        return BusinessSearchRequest(
            search_term=search_term,
            location=location,
            price_categories=price_categories,
            categories=categories,
            attributes=attributes,
            radius=radius,
        )

    session_id: str = Column(
        String(length=36), ForeignKey("search_session.id"), primary_key=True
    )
    search_term: str = Column(String(length=1000))
    lat: float = Column(Float)
    long: float = Column(Float)
    location: Location = composite(Location, lat, long)
    price_categories: [PriceCategory] = Column(PickleType)
    categories: [str] = Column(PickleType)
    attributes: [str] = Column(PickleType)
    radius: float = Column(Float)
