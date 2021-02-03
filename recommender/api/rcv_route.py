from typing import Dict

from flask import Blueprint, Response, request

from recommender.api import json_content_type
from recommender.api.global_services import business_manager, auth_route_utils
from recommender.data.auth.user import SerializableBasicUser
from recommender.data.rcv.candidate import Candidate
from recommender.data.rcv.election import Election
from recommender.data.rcv.election_status import ElectionStatus
from recommender.rcv.rcv_manager import RCVManager

rcv_manager = RCVManager(business_manager)

rcv = Blueprint("rcv", __name__)


@rcv.route("", methods=["PUT"])
@auth_route_utils.use_or_create_user_route
def new_rcv(user: SerializableBasicUser) -> Dict[str, Dict[str, str]]:
    election = rcv_manager.create_election(user=user)

    data = {"election": {
        "id": election.id,
        "activeCode": election.active_id
    }}

    return data


@rcv.route("", methods=["GET"])
@json_content_type()
def get_active_election_info() -> [Candidate]:
    # switch over to use query parameters to determine fields
    # update to return displayable businesses
    active_id = request.json["electionCode"]
    return rcv_manager.get_candidates(active_id)

@rcv.route("/<election_id>", methods=["GET"])
@json_content_type()
def get_election(election_id: str) -> Election:
    output = rcv_manager.get_election_by_id(election_id)
    return output


@rcv.route("/<election_id>/updates", methods=["GET"])
def subscribe_to_election_updates(election_id: str) -> Response:
    return Response(
        response=rcv_manager.get_election_update_stream(election_id).subscribe_to_raw(),
        mimetype="text/event-stream",
    )


@rcv.route("/add-candidate", methods=["PUT"])
@auth_route_utils.require_user_route()
def add_candidate(user: SerializableBasicUser) -> Dict[str, bool]:
    election_code = request.json["electionCode"]
    business_id = request.json["businessId"]

    already_added = not rcv_manager.add_candidate(
        active_id=election_code, business_id=business_id, user_id=user.id
    )
    return {"alreadyAdded": already_added}


@rcv.route("/<election_id>/state", methods=["POST"])
@auth_route_utils.require_user_route()
def update_election_state(user: SerializableBasicUser, election_id: str) -> Response:
    # Verify auth updating state is the one who created the election
    new_state = request.json["state"]
    if (
            new_state != ElectionStatus.VOTING.value
            and new_state != ElectionStatus.MANUALLY_COMPLETE.value
    ):
        raise ValueError(f"Invalid input state: {new_state}")

    if new_state == ElectionStatus.VOTING.value:
        rcv_manager.move_election_to_voting(election_id)
    elif new_state == ElectionStatus.MANUALLY_COMPLETE.value:
        rcv_manager.mark_election_as_complete(
            election_id, ElectionStatus.MANUALLY_COMPLETE
        )
    return Response(status=200)


@rcv.route("/<election_id>/vote", methods=["PUT"])
@auth_route_utils.require_user_route()
def vote(election_id: str, user: SerializableBasicUser) -> Response:
    # Verify auth updating state is the one who created the election
    votes: [str] = request.json["votes"]
    rcv_manager.vote(user_id=user.id, election_id=election_id, votes=votes)
    return Response(status=201)
