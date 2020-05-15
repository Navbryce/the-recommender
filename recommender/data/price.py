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

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "FREE" if self == PriceCategory.FREE else self.get_api_return_value()

    # The value returned for "price" in the API is different from the value used to filter results
    def get_api_return_value(self) -> Optional[str]:
        return (
            None
            if self == PriceCategory.FREE
            else "".join(["$" for value in range(self.value)])
        )

    @staticmethod
    def from_category_string(category_string: Optional[str]):
        if category_string not in PRICE_RETURN_VALUE_TO_CATEGORY:
            raise ValueError("Unknown value category: " + category_string)
        return PRICE_RETURN_VALUE_TO_CATEGORY[category_string]


PRICE_RETURN_VALUE_TO_CATEGORY = {
    priceCategory.get_api_return_value(): priceCategory
    for priceCategory in PriceCategory
}
