from enum import Enum, unique
from typing import Optional


@unique
class PriceCategory(Enum):
    # Value is filter value in api
    FREE = None
    LOW = 1
    MID_LOW = 2
    MID_HIGH = 3
    HIGH = 4

    @staticmethod
    def from_name(enum_name: str):
        if enum_name not in PRICE_CATEGORY_NAME_TO_CATEGORY:
            raise ValueError("Unknown name for enum: " + enum_name)
        return PRICE_CATEGORY_NAME_TO_CATEGORY[enum_name]

    @staticmethod
    def from_api_return_value(category_string: Optional[str]):
        if category_string not in PRICE_RETURN_VALUE_TO_CATEGORY:
            raise ValueError("Unknown value category: " + category_string)
        return PRICE_RETURN_VALUE_TO_CATEGORY[category_string]

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.name

    def get_yelp_api_filter_value(self):
        return self.value

    # The value returned for "price" in the API is different from the value used to filter results
    def get_yelp_api_return_value(self) -> Optional[str]:
        return (
            None
            if self == PriceCategory.FREE
            else "".join(["$" for value in range(self.value)])
        )


PRICE_RETURN_VALUE_TO_CATEGORY = {
    priceCategory.get_yelp_api_return_value(): priceCategory
    for priceCategory in PriceCategory
}

PRICE_CATEGORY_NAME_TO_CATEGORY = {
    priceCategory.name: priceCategory for priceCategory in PriceCategory
}
