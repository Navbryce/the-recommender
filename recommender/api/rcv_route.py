from typing import Optional

from flask import Blueprint, Response, request

from recommender.api.global_services import business_manager
from recommender.api.utils.auth_route_utils import AuthRouteUtils
from recommender.api.utils.json_content_type import generate_json_response
from recommender.data.rcv.election_status import ElectionStatus
from recommender.data.recommendation.location import Location
from recommender.data.user.user import SerializableBasicUser
from recommender.data.user.user_manager import UserManager
from recommender.rcv.rcv_manager import RCVManager

user_manager = UserManager()
auth_route_utils = AuthRouteUtils(user_manager)
rcv_manager = RCVManager(business_manager)

rcv = Blueprint("rcv", __name__)


@rcv.route("", methods=["PUT"])
@auth_route_utils.get_user_route
def new_rcv(user_maybe: Optional[SerializableBasicUser]) -> Response:
    location = Location.from_json(request.json["location"])
    user = (
        user_maybe
        if user_maybe is not None
        else user_manager.create_anonymous_user_and_generate_name().to_serializable_user()
    )
    election = rcv_manager.create_election(location=location, user=user)

    data = {"election": {"id": election.id, "activeCode": election.active_id}}

    if user_maybe is None:
        data["createdUser"] = {"id": user.id, "nickname": user.nickname}

    response = generate_json_response(data=data)

    if user_maybe is None:
        auth_route_utils.login_as_user(response, user)

    return response


@rcv.route("/add-candidate", methods=["PUT"])
@auth_route_utils.get_user_route
def add_candidate(user_maybe: Optional[SerializableBasicUser]) -> Response:
    # Create anonymous user if user not logged in
    election_code = request.json["electionCode"]
    business_id = request.json["businessId"]

    already_added = not rcv_manager.add_candidate(
        active_id=election_code, business_id=business_id
    )
    return generate_json_response(data={"alreadyAdded": already_added})


@rcv.route("/<election_id>/state", methods=["POST"])
def update_election_state(election_id: str):
    # Verify user updating state is the one who created the election
    new_state = request.json["state"]
    if new_state == ElectionStatus.VOTING.value:
        rcv_manager.move_election_to_voting(election_id)
    elif new_state == ElectionStatus.MANUALLY_COMPLETE.value:
        rcv_manager.mark_election_as_complete(
            election_id, ElectionStatus.MANUALLY_COMPLETEcommit
        )
    else:
        raise ValueError(f"Invalid input state: {new_state}")


@rcv.route("/<election_id>/vote", methods=["PUT"])
@auth_route_utils.get_user_route
def vote(election_id: str):
    # Verify user updating state is the one who created the election
    new_state = request.json["state"]
    if new_state == ElectionStatus.VOTING.value:
        rcv_manager.move_election_to_voting(election_id)
    elif new_state == ElectionStatus.MANUALLY_COMPLETE.value:
        rcv_manager.mark_election_as_complete(
            election_id, ElectionStatus.MANUALLY_COMPLETEcommit
        )
    else:
        raise ValueError(f"Invalid input state: {new_state}")
