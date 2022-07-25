from typing import Dict, Optional

from flask import Blueprint, Response, request

from recommender.api import json_content_type
from recommender.api.global_services import (
    auth_route_utils,
    business_manager,
    user_manager,
)
from recommender.data.auth.user import SerializableBasicUser
from recommender.data.rcv.election import Election
from recommender.data.rcv.election_metadata_response import ElectionMetadataResponse
from recommender.data.rcv.election_result import DisplayableElectionResult
from recommender.data.rcv.election_status import ElectionStatus
from recommender.db_config import DbSession
from recommender.rcv.rcv_manager import RCVManager

rcv_manager = RCVManager(business_manager, user_manager)

rcv = Blueprint("rcv", __name__)


@rcv.route("", methods=["PUT"])
@auth_route_utils.require_user_route()
@json_content_type()
def new_rcv(user: SerializableBasicUser) -> ElectionMetadataResponse:
    session = DbSession()
    try:
        return election_to_metadata_response(rcv_manager.create_election(session, user=user))
    finally:
        session.close()


@rcv.route("", methods=["GET"])
@json_content_type()
def get_active_election_metadata() -> Optional[ElectionMetadataResponse]:
    session = DbSession()
    try:
        active_id = request.json["electionCode"]
        election = rcv_manager.get_active_election_by_active_id(session, active_id=active_id)
        if election is None:
            return None
        return election_to_metadata_response(election)
    finally:
        session.close()


def election_to_metadata_response(election: Election) -> ElectionMetadataResponse:
    return ElectionMetadataResponse(
        id=election.id,
        active_id=election.active_id,
        election_status=election.election_status,
    )


@rcv.route("/<election_id>", methods=["GET"])
@json_content_type()
def get_election(election_id: str) -> Optional[Election]:
    with_voters = request.args.get("withVoters", True)
    db_session = DbSession()
    try:
        return rcv_manager.get_displayable_election_by_id(db_session, election_id, with_voters)
    finally:
        db_session.close()


# TODO: Maybe deprecate route with the fetch election route
@rcv.route("/<election_id>/results", methods=["GET"])
@json_content_type()
def get_election_results(election_id: str) -> Optional[DisplayableElectionResult]:
    db_session = DbSession()
    try:
        return rcv_manager.get_election_results(db_session, election_id)
    finally:
        db_session.close()


@rcv.route("/<election_id>/updates", methods=["GET"])
def subscribe_to_election_updates(election_id: str) -> Response:
    db_session = DbSession()
    try:
        return Response(
            response=rcv_manager.get_election_update_stream(db_session, election_id).subscribe_to_raw(),
            mimetype="text/event-stream",
        )
    finally:
        db_session.close()


@rcv.route("/add-candidate", methods=["PUT"])
@auth_route_utils.require_user_route()
def add_candidate(user: SerializableBasicUser) -> Dict[str, bool]:
    election_code = request.json["electionCode"]
    business_id = request.json["businessId"]

    db_session = DbSession()
    try:
        already_added = not rcv_manager.add_candidate(
            db_session, active_id=election_code, business_id=business_id, user_id=user.id
        )
        return {"alreadyAdded": already_added}
    finally:
        db_session.close()


@rcv.route("/<election_id>/state", methods=["PUT"])
@auth_route_utils.require_user_route()
def update_election_state(user: SerializableBasicUser, election_id: str) -> Response:
    # TODO: Verify auth updating state is the one who created the election
    new_state = request.json["state"]
    if (
            new_state != ElectionStatus.VOTING.value
            and new_state != ElectionStatus.COMPLETE.value
    ):
        raise ValueError(f"Invalid input state: {new_state}")

    db_session = DbSession()
    try:
        if new_state == ElectionStatus.VOTING.value:
            rcv_manager.move_election_to_voting(db_session, election_id)
        elif new_state == ElectionStatus.COMPLETE.value:
            rcv_manager.mark_election_as_complete(
                db_session,
                election_id
            )
        return Response(status=200)
    finally:
        db_session.close()


@rcv.route("/<election_id>/vote", methods=["PUT"])
@auth_route_utils.require_user_route()
def vote(election_id: str, user: SerializableBasicUser) -> Response:
    # Verify auth updating state is the one who created the election
    votes: [str] = request.json["votes"]

    db_session = DbSession()
    try:
        rcv_manager.vote(db_session, user_id=user.id, election_id=election_id, votes=votes)
        return Response(status=201)
    finally:
        db_session.close()
