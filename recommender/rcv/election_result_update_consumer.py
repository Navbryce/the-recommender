from collections import Counter
import random
from typing import Final, Tuple, List, Dict

from recommender.api.utils.server_sent_event import ServerSentEvent
from recommender.data.rcv.candidate_round_result import CandidateRoundResult
from recommender.data.rcv.election import Election
from recommender.data.rcv.round import Round
from recommender.data.rcv.round_action import RoundAction
from recommender.db_config import DbSession
from recommender.rcv.election_update_stream import (
    ElectionUpdateStream,
    ElectionUpdateEventType,
)
from recommender.rcv.rcv_queue_config import rcv_vote_queue

"""
Switch over to use messaging queues

Shard by election ID -- currently not done (OPTIONAL)
"""


class ElectionResultUpdateConsumer:
    QUEUE_NAME: Final[str] = rcv_vote_queue.name

    def consume(self, election_id: str):
        db_session = DbSession()
        Election.delete_election_results_for_election(db_session, election_id)
        db_session.flush()
        db_session.commit()
        rankings_by_voter: Dict[
            str, List[str]
        ] = Election.get_rankings_by_user_for_election(db_session, election_id)
        self.__run_election_round(
            db_session=db_session,
            election_id=election_id,
            rankings=list(rankings_by_voter.values()),
        )
        db_session.commit()
        ElectionUpdateStream.for_election(election_id).publish_message(
            ServerSentEvent(
                type=ElectionUpdateEventType.RESULTS_UPDATED, payload=None
            )
        )

    def __run_election_round(
        self,
        db_session: DbSession,
        election_id: str,
        rankings: List[List[str]],
        round=0,
    ):
        total_votes = len(rankings)

        first_vote_counts = self.__count_first_ranks(rankings)
        vote_items = first_vote_counts.items()

        most_voted, most_first_one_votes = max(vote_items, key=lambda x: x[1])

        if most_first_one_votes > total_votes / 2:
            self.__write_round_to_database(
                db_session=db_session,
                election_id=election_id,
                votes=vote_items,
                round=round,
                affected_candidate=most_voted,
                candidate_round_action=RoundAction.WON,
            )
        elif (
            most_first_one_votes == total_votes / 2
            and len(first_vote_counts.keys()) == 2
        ):
            self.__write_round_to_database(
                db_session=db_session,
                election_id=election_id,
                votes=vote_items,
                round=round,
                affected_candidate=list(first_vote_counts.keys())[
                    random.randrange(0, 2)
                ],
                candidate_round_action=RoundAction.WON_VIA_TIEBREAKER,
            )
        else:
            least_voted, least_first_one_votes = min(vote_items, key=lambda x: x[1])
            self.__write_round_to_database(
                db_session=db_session,
                election_id=election_id,
                votes=vote_items,
                round=round,
                affected_candidate=least_voted,
                candidate_round_action=RoundAction.ELIMINATED,
            )
            self.__eliminate_candidate(rankings, least_voted)
            self.__run_election_round(
                db_session=db_session,
                election_id=election_id,
                rankings=rankings,
                round=round + 1,
            )

    def __count_first_ranks(self, rankings: List[List[str]]) -> Counter:
        vote_counters = Counter({candidate: 0 for candidate in list(rankings[0])})
        for ranking in rankings:
            vote_counters[ranking[0]] += 1
        return vote_counters

    def __write_round_to_database(
        self,
        db_session: DbSession,
        election_id: str,
        votes: List[Tuple[str, int]],
        round: int,
        affected_candidate: str,
        candidate_round_action: RoundAction,
    ):
        db_session.add(Round(election_id=election_id, round_number=round))
        db_session.flush()
        db_session.add_all(
            [
                CandidateRoundResult(
                    election_id=election_id,
                    round_number=round,
                    business_id=candidate_id,
                    number_of_rank_one_votes=number_of_rank_one_votes_for_candidate,
                    round_action=None
                    if candidate_id != affected_candidate
                    else candidate_round_action,
                )
                for candidate_id, number_of_rank_one_votes_for_candidate in votes
            ]
        )
        db_session.flush()

    """
    Modifies rankings in-place
    """

    def __eliminate_candidate(self, rankings: List[List[str]], candidate_id: str):
        for ranking in rankings:
            ranking.remove(candidate_id)
