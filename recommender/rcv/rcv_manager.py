import random
from collections import Generator
from datetime import datetime
from uuid import uuid4

import requests
from rq.job import JobStatus
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import load_only

from recommender.api.utils.http_exception import HttpException, ErrorCode
from recommender.business.business_manager import BusinessManager
from recommender.data.db_utils import is_unique_key_error
from recommender.data.rcv.candidate import Candidate
from recommender.data.rcv.election import Election, ACTIVE_ID_LENGTH
from recommender.data.rcv.election_status import ElectionStatus
from recommender.data.rcv.ranking import Ranking
from recommender.data.recommendation.location import Location
from recommender.data.auth.user import SerializableBasicUser
from recommender.db_config import DbSession
from recommender.rcv.election_update_stream import (
    ElectionUpdateStream,
    ElectionUpdateEvent,
    ElectionUpdateEventType,
)
from recommender.rcv.rcv_queue_config import rcv_vote_queue
from recommender.rcv.election_result_update_consumer import ElectionResultUpdateConsumer


class RCVManager:
    __business_manager: BusinessManager
    __election_result_update_consumer: ElectionResultUpdateConsumer = ElectionResultUpdateConsumer()

    def __init__(self, business_manager: BusinessManager):
        self.__business_manager = business_manager

    def create_election(
        self, location: Location, user: SerializableBasicUser
    ) -> Election:
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
            raise InvalidElectionStateException(
                message=f"Cannot add a candidate to an election with status: {partial_election.election_status.value}"
            )

        # Verify business exists? Cache business
        # Calculate distance

        candidate = Candidate(
            election_id=partial_election.id,
            business_id=business_id,
            distance=0,
            creator_id=user_id,
        )
        db_session.add(candidate)
        try:
            db_session.commit()
        except IntegrityError as error:
            if is_unique_key_error(error):
                return False
            raise error
        ElectionUpdateStream.for_election(partial_election.id).publish_message(
            ElectionUpdateEvent(
                type=ElectionUpdateEventType.CANDIDATE_ADDED, payload=business_id
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
        if partial_election.election_status != ElectionStatus.IN_CREATION:
            raise InvalidElectionStateException(
                message=f"Cannot move an election to status {ElectionStatus.VOTING.name} when status is {partial_election.election_status.value}"
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
            query_modifier=lambda x: x.options(
                load_only(Election.id, Election.election_status)
            ),
        )
        if partial_election.election_status != ElectionStatus.VOTING:
            raise InvalidElectionStateException(
                message=f"Cannot move an election to complete with status: {partial_election.election_status.value}"
            )
        partial_election.election_status = complete_reason
        partial_election.election_completed_at = datetime.now()
        db_session.commit()

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
            raise InvalidElectionStateException(
                f"Cannot vote unless election is in voting status. Current status: {partial_election.election_status.name}"
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


class InvalidElectionStateException(HttpException):
    def __init__(self, message):
        super(InvalidElectionStateException, self).__init__(
            message=message,
            status_code=requests.codes.conflict,
            error_code=ErrorCode.INVALID_ELECTION_STATUS,
        )
