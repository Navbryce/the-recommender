import json
import random
from datetime import datetime
from typing import Optional
from uuid import uuid4

from rq.job import JobStatus
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import load_only

from recommender.api.utils.http_exception import ErrorCode, HttpException
from recommender.auth.user_manager import UserManager
from recommender.business.business_manager import BusinessManager
from recommender.data.auth.user import SerializableBasicUser
from recommender.data.business.displayable_business import DisplayableBusiness
from recommender.data.db_utils import is_unique_key_error
from recommender.data.rcv.candidate import Candidate
from recommender.data.rcv.displayable_election import (
    DisplayableCandidate,
    DisplayableElection,
)
from recommender.data.rcv.election import ACTIVE_ID_LENGTH, Election
from recommender.data.rcv.election_result import (
    DisplayableElectionResult,
    ElectionResult,
)
from recommender.data.rcv.election_status import ElectionStatus
from recommender.data.rcv.ranking import Ranking
from recommender.db_config import DbSession
from recommender.rcv.election_result_update_consumer import ElectionResultUpdateConsumer
from recommender.rcv.election_update_stream import (
    CandidateAddedEvent,
    ElectionUpdateStream,
    StatusChangedEvent,
)
from recommender.rcv.rcv_queue_config import rcv_vote_queue
from recommender.utilities.json_encode_utilities import NoNormalizationDict


class RCVManager:
    __business_manager: BusinessManager
    __election_result_update_consumer: ElectionResultUpdateConsumer = ElectionResultUpdateConsumer()
    __user_manager: UserManager

    def __init__(self, business_manager: BusinessManager, user_manager: UserManager):
        self.__business_manager = business_manager
        self.__user_manager = user_manager

    def create_election(self, user: SerializableBasicUser) -> Election:
        db_session = DbSession()
        election_id = str(uuid4())
        while True:
            try:
                election = Election(
                    id=election_id,
                    active_id=self.__generate_election_active_id(),
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

    def get_displayable_election_by_id(self, id: str) -> Optional[DisplayableElection]:
        db_session = DbSession()
        election = Election.get_election_by_id(db_session=db_session, id=id)
        if election is None:
            return None
        return DisplayableElection(
            id=election.id,
            active_id=election.active_id,
            election_status=election.election_status,
            candidates=[
                DisplayableCandidate(
                    business_id=candidate.business_id,
                    name=self.__business_manager.get_displayable_business(
                        candidate.business_id
                    ).name,
                    nominator_nickname=candidate.nominator.nickname,
                )
                for candidate in election.candidates
            ],
        )

    def get_active_election_by_active_id(self, active_id: str) -> Election:
        db_session = DbSession()
        return Election.get_active_election_by_active_id(db_session, active_id)

    def get_election_results(self, id: str) -> DisplayableElectionResult:
        db_session = DbSession()
        result_as_string = Election.get_election_by_id(
            db_session, id, lambda x: x.options(load_only(Election.election_result))
        ).election_result
        # TODO: Deserializes string just to re-serialize it. Change it in the future
        if result_as_string is None:
            return None
        results = json.loads(result_as_string)
        # TODO: Maybe smoothe JSON decoding/encoding for database
        return DisplayableElectionResult.from_election_result(
            ElectionResult(
                calculated_at=results["calculated_at"], rounds=results["rounds"]
            )
        )

    def add_candidate(self, active_id: str, business_id: str, user_id: str) -> bool:
        db_session = DbSession()

        partial_election = Election.get_active_election_by_active_id(
            db_session=db_session,
            active_id=active_id,
            query_modifier=lambda x: x.options(
                load_only(Election.id, Election.election_status)
            ),
        )
        if partial_election is None:
            raise HttpException(
                message=f"Election with active id: {active_id} not found",
                status_code=404,
            )
        if partial_election.election_status != ElectionStatus.IN_CREATION:
            raise InvalidElectionStatusException(
                message=f"Cannot add a candidate to an election with current status",
                status=partial_election.election_status,
            )

        # Verify business exists? Cache business
        # Calculate distance

        candidate = Candidate(
            election_id=partial_election.id,
            business_id=business_id,
            distance=0,
            nominator_id=user_id,
        )
        db_session.add(candidate)
        try:
            db_session.commit()
        except IntegrityError as error:
            if is_unique_key_error(error):
                return False
            raise error
        # TODO: Accelerate fetching process here
        business: DisplayableBusiness = self.__business_manager.get_displayable_business(
            business_id=business_id
        )
        # TODO: Maybe just pass the name stored within the cookie instead of refetching from the database
        nickname = self.__user_manager.get_nickname_by_user_id(user_id)
        ElectionUpdateStream.for_election(partial_election.id).publish_message(
            CandidateAddedEvent(
                business_id=business_id,
                name=business.name,
                nominator_nickname=nickname if nickname is not None else "Unknown",
            )
        )
        return True

    def move_election_to_voting(self, election_id: str):
        db_session = DbSession()
        partial_election = Election.get_election_by_id(
            db_session,
            election_id,
            query_modifier=lambda x: x.options(
                load_only(Election.id, Election.election_status)
            ),
        )
        if partial_election is None:
            raise HttpException(
                message=f"Election with election id: {election_id} not found",
                status_code=404,
            )
        # TODO: Refactor election status "is already status" check (not changing) for both move_election_to_voting and
        #  mark_as_complete into one function that fetches the partial electoin
        if partial_election.election_status == ElectionStatus.VOTING:
            return
        if partial_election.election_status != ElectionStatus.IN_CREATION:
            raise InvalidElectionStatusException(
                message=f"Cannot move an election to status {ElectionStatus.VOTING.name} with current status",
                status=partial_election.status,
            )

        # TODO: validate change made by using WHERE
        partial_election.election_status = ElectionStatus.VOTING
        db_session.commit()
        self.__push_election_status_change_to_update_stream(
            election_id, ElectionStatus.VOTING
        )

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
            query_modifier=lambda x: x.options(
                load_only(Election.id, Election.election_status)
            ),
        )
        if partial_election == complete_reason:
            return

        if partial_election.election_status != ElectionStatus.VOTING:
            raise InvalidElectionStatusException(
                message=f"Cannot move an election to complete with current status",
                status=partial_election.election_status,
            )
        partial_election.election_status = complete_reason
        partial_election.election_completed_at = datetime.now()
        db_session.commit()
        self.__push_election_status_change_to_update_stream(
            election_id, complete_reason
        )

    def __push_election_status_change_to_update_stream(
        self, election_id: str, new_status: ElectionStatus
    ):
        ElectionUpdateStream.for_election(election_id).publish_message(
            StatusChangedEvent(new_status)
        )

    def get_candidates(self, active_id: str) -> [Candidate]:
        db_session = DbSession()
        partial_election = Election.get_active_election_by_active_id(
            db_session,
            active_id,
            query_modifier=lambda x: x.options(load_only(Election.id)),
        )

        if partial_election is None:
            raise HttpException(
                message=f"Election with active id: {active_id} not found",
                status_code=404,
            )
        return partial_election.candidates

    def vote(self, user_id: str, election_id: str, votes: [str]):
        db_session = DbSession()
        partial_election = Election.get_election_by_id(
            db_session,
            election_id,
            query_modifier=lambda x: x.options(
                load_only(Election.id, Election.election_status)
            ),
        )

        if partial_election is None:
            raise HttpException(
                message=f"Election with id: {election_id} not found", status_code=404
            )

        if partial_election.election_status != ElectionStatus.VOTING:
            raise InvalidElectionStatusException(
                f"Cannot vote unless election is in voting status with current status",
                status=partial_election.election_status,
            )

        candidate_ids = set(
            [candidate.business_id for candidate in partial_election.candidates]
        )
        for business_id in votes:
            if business_id not in candidate_ids:
                raise HttpException(
                    message=f"Unknown or duplicate candidate id {business_id}",
                    status_code=404,
                )
            candidate_ids.remove(business_id)

        if len(candidate_ids) > 0:
            raise HttpException(
                message=f"Missing votes for candidates: {', '.join(candidate_ids)}",
                status_code=400,
            )

        rankings = [
            Ranking(
                user_id=user_id,
                election_id=election_id,
                business_id=business_id,
                rank=index,
            )
            for index, business_id in enumerate(votes)
        ]
        Ranking.delete_users_rankings_for_election(
            db_session, user_id=user_id, election_id=election_id
        )
        db_session.add_all(rankings)
        db_session.commit()

        self.__queue_election_for_result_update(election=partial_election)

    def __queue_election_for_result_update(self, election: Election):
        """
        Add more logic later on:
        If election has been updated recently, delay update by a bit or add some sort of rate limit on an
        election basis
        """
        fetch_result = rcv_vote_queue.fetch_job(election.id)
        # TODO: Watch for stalled jobs
        if (
            fetch_result is None
            or fetch_result.get_status(refresh=False) == JobStatus.FINISHED
            or fetch_result.get_status(refresh=False) == JobStatus.FAILED
        ):
            rcv_vote_queue.enqueue(
                self.__election_result_update_consumer.consume,
                election.id,
                job_id=election.id,
            )

    def get_election_update_stream(self, election_id: str) -> ElectionUpdateStream:
        db_session = DbSession()
        if (
            Election.get_election_by_id(
                db_session, election_id, lambda x: x.options(load_only(Election.id))
            )
            is None
        ):
            raise HttpException(
                message=f"Election with id: {election_id} not found", status_code=404
            )

        return ElectionUpdateStream.for_election(election_id)


class InvalidElectionStatusException(HttpException):
    def __init__(
        self, message: str, status: ElectionStatus, election_id: Optional[str]
    ):
        super(InvalidElectionStatusException, self).__init__(
            message=message,
            error_code=ErrorCode.INVALID_ELECTION_STATUS,
            additional_data={"status": status, "election_id": election_id},
        )
