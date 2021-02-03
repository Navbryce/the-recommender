from flask import Blueprint, request

from recommender.api import json_content_type
from recommender.api.global_services import business_manager
from recommender.data.business.localized_business import LocalizedBusiness

business = Blueprint("business", __name__)


@business.route("/localized", methods=["GET"])
@json_content_type()
def get_localized_businesses() -> [LocalizedBusiness]:
    business_ids = request.args['ids'].split(',')
    return [
        business_manager.get_localized_business(id) for id in business_ids
    ]
