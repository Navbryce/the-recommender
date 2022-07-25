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
from recommender.data.auth.displayable_user import DisplayableUser
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
    StatusChangedEvent, VoteCastEvent,
)
from recommender.rcv.rcv_queue_config import rcv_vote_queue


class RCVManager:
    __business_manager: BusinessManager
    __election_result_update_consumer: ElectionResultUpdateConsumer = ElectionResultUpdateConsumer()
    __user_manager: UserManager

    def __init__(self, business_manager: BusinessManager, user_manager: UserManager):
        self.__business_manager = business_manager
        self.__user_manager = user_manager

    def create_election(self, db_session: DbSession, user: SerializableBasicUser) -> Election:
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

    def get_displayable_election_by_id(self, db_session: DbSession, id: str, with_voters=False) -> Optional[
        DisplayableElection]:

        election = Election.get_election_by_id(db_session=db_session, id=id)
        if election is None:
            return None

        optional_props = {}
        if with_voters:
            optional_props["voters"] = [DisplayableUser.from_user(user) for user in election.voters]

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
            **optional_props
        )

    def get_active_election_by_active_id(self, db_session: DbSession, active_id: str) -> Election:
        return Election.get_active_election_by_active_id(db_session, active_id)

    def get_election_results(self, db_session: DbSession, id: str) -> Optional[DisplayableElectionResult]:
        results = Election.get_election_by_id(
            db_session, id, lambda x: x.options(load_only(Election.election_result))
        ).election_result
        if results is None:
            return None
        return DisplayableElectionResult.from_election_result(
            ElectionResult(
                calculated_at=results.calculated_at, rounds=results.rounds
            )
        )

    def add_candidate(self, db_session: DbSession, active_id: str, business_id: str, user_id: str) -> bool:
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
        nickname = self.__user_manager.get_nickname_by_user_id(db_session, user_id)
        ElectionUpdateStream.for_election(partial_election.id).publish_message(
            CandidateAddedEvent(
                business_id=business_id,
                name=business.name,
                nominator_nickname=nickname if nickname is not None else "Unknown",
            )
        )
        return True

    def move_election_to_voting(self, db_session: DbSession, election_id: str):
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
            # do nothing if already in voting status voting
            return
        if partial_election.election_status != ElectionStatus.IN_CREATION:
            raise InvalidElectionStatusException(
                election_id=election_id,
                status=partial_election.status,
                message=f"Cannot move an election to status {ElectionStatus.VOTING.name} with current status",
            )

        if Election.get_number_of_candidates(db_session, election_id) == 0:
            raise InvalidElectionStatusException(
                election_id=election_id,
                status=partial_election.election_status,
                message=f"Cannot move election to status {ElectionStatus.VOTING.name} "
                        f"when no candidates have been nominated")

        # TODO: validate change made by using WHERE
        partial_election.election_status = ElectionStatus.VOTING
        db_session.commit()
        self.__push_election_status_change_to_update_stream(
            election_id, ElectionStatus.VOTING
        )

    def mark_election_as_complete(
            self, db_session: DbSession, election_id: str
    ):
        # could lead to race conditions, but exact completed_at not support important
        partial_election = Election.get_election_by_id(
            db_session,
            election_id,
            query_modifier=lambda x: x.options(
                load_only(Election.id, Election.election_status)
            ),
        )
        if partial_election.election_status == ElectionStatus.COMPLETE:
            return

        if partial_election.election_status != ElectionStatus.VOTING:
            raise InvalidElectionStatusException(
                message=f"Cannot move an election to complete with current status",
                status=partial_election.election_status,
            )
        partial_election.election_status = ElectionStatus.COMPLETE
        partial_election.election_completed_at = datetime.now()
        db_session.commit()
        self.__queue_election_for_result_update(election=partial_election)
        self.__push_election_status_change_to_update_stream(election_id, ElectionStatus.COMPLETE)

    def __push_election_status_change_to_update_stream(
            self, election_id: str, new_status: ElectionStatus
    ):
        ElectionUpdateStream.for_election(election_id).publish_message(
            StatusChangedEvent(new_status)
        )

    def get_candidates(self, db_session: DbSession, active_id: str) -> [Candidate]:
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

    def vote(self, db_session: DbSession, user_id: str, election_id: str, votes: [str]):
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
        already_voted = Ranking.delete_users_rankings_for_election(
            db_session, user_id=user_id, election_id=election_id
        ) > 0
        db_session.add_all(rankings)
        db_session.commit()

        if not already_voted:
            # TODO: Maybe pass nickname from cookie instead of re-fetching after vote
            nickname = self.__user_manager.get_nickname_by_user_id(db_session, user_id)
            ElectionUpdateStream.for_election(election_id).publish_message(
                VoteCastEvent(
                    user_id=user_id,
                    nickname=nickname if nickname is not None else "Unknown"
                )
            )

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

    def get_election_update_stream(self, db_session: DbSession, election_id: str) -> ElectionUpdateStream:
        """
        checks election existence.

        :param db_session: database session to use
        :param election_id:
        :return: if the election exists, returns the ElectionUpdateStream
        """
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
            self, message: str, status: ElectionStatus, election_id: Optional[str] = None
    ):
        super(InvalidElectionStatusException, self).__init__(
            message=message,
            error_code=ErrorCode.INVALID_ELECTION_STATUS,
            additional_data={"status": status, "election_id": election_id},
        )
