import random
from datetime import datetime
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import load_only

from recommender.api.utils.http_exception import HttpException, ErrorCode
from recommender.business.business_manager import BusinessManager
from recommender.data.db_utils import is_unique_key_error
from recommender.data.rcv.candidate import Candidate
from recommender.data.rcv.election import Election, ACTIVE_ID_LENGTH
from recommender.data.rcv.election_status import ElectionStatus
from recommender.data.recommendation.location import Location
from recommender.data.user.user import BasicUser
from recommender.db_config import DbSession
from recommender.data.rcv.candidate_round_result import CandidateRoundResult


class RCVManager:
    __business_manager: BusinessManager

    def __init__(self, business_manager: BusinessManager):
        self.__business_manager = business_manager

    def create_election(self, location: Location, user: BasicUser) -> Election:
        db_session = DbSession()
        election_id = str(uuid4())
        while True:
            try:
                election = Election(
                    id=election_id,
                    active_id=self.__generate_election_active_id(),
                    location=location,
                    election_creator_id=user.id,
                )
                db_session.add(election)
                db_session.commit()
                return election
            except BaseException as error:
                raise error

    STARTING_LETTER_CHAR: int = ord("a")
    RANGE = ord("z") - STARTING_LETTER_CHAR

    def __generate_election_active_id(self) -> str:
        return "".join(
            [
                chr(self.STARTING_LETTER_CHAR + random.randrange(self.RANGE + 1))
                for index in range(ACTIVE_ID_LENGTH)
            ]
        )

    def add_candidate(self, active_id: str, business_id: str) -> bool:
        db_session = DbSession()

        partial_election = Election.get_active_election_by_active_id(
            db_session=db_session,
            active_id=active_id,
            query_modifier=lambda x: x.options(load_only("id", "election_status")),
        )
        if partial_election is None:
            raise HttpException(
                message=f"Election with active id: {active_id} not found",
                status_code=404,
            )
        if partial_election.election_status != ElectionStatus.IN_CREATION:
            raise InvalidElectionStateException(
                message=f"Cannot add a candidate to an election with status: {partial_election.election_status.value}"
            )

        # Verify business exists? Cache business
        # Calculate distance

        candidate = Candidate(
            election_id=partial_election.id, business_id=business_id, distance=0
        )
        db_session.add(candidate)
        try:
            db_session.commit()
        except IntegrityError as error:
            if is_unique_key_error(error):
                return False
            raise error
        return True

    def move_election_to_voting(self, election_id: str):
        db_session = DbSession()
        partial_election = Election.get_election_by_id(
            db_session,
            election_id,
            query_modifier=lambda x: x.options(load_only("id", "election_status")),
        )
        if partial_election is None:
            raise HttpException(
                message=f"Election with election id: {election_id} not found",
                status_code=404,
            )
        if partial_election.election_status != ElectionStatus.IN_CREATION:
            raise InvalidElectionStateException(
                message=f"Cannot move an election to voting with status: {partial_election.election_status.value}"
            )

        partial_election.election_status = ElectionStatus.VOTING
        db_session.commit()

    def mark_election_as_complete(
        self, election_id: str, complete_reason: ElectionStatus
    ):
        if (
            complete_reason != ElectionStatus.MANUALLY_COMPLETE
            or complete_reason != ElectionStatus.MARKED_COMPLETE
        ):
            raise ValueError(f"Invalid complete reason: {complete_reason.value}")

        db_session = DbSession()
        # could lead to race conditions, but exact completed_at not support important
        partial_election = Election.get_election_by_id(
            db_session,
            election_id,
            query_modifier=lambda x: x.options(load_only("id", "election_status")),
        )
        if partial_election.election_status != ElectionStatus.VOTING:
            raise InvalidElectionStateException(
                message=f"Cannot move an election to complete with status: {partial_election.election_status.value}"
            )
        partial_election.election_status = complete_reason
        partial_election.election_completed_at = datetime.now()
        db_session.commit()


class InvalidElectionStateException(HttpException):
    def __init__(self, message):
        super(InvalidElectionStateException, self).__init__(
            message=message,
            status_code=401,
            error_code=ErrorCode.INVALID_ELECTION_STATUS,
        )
