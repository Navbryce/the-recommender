import random
from collections import Counter
from time import sleep
from typing import Dict, Final, List

from recommender.data.rcv.election import Election
from recommender.data.rcv.election_result import (
    CandidateRoundResult,
    DisplayableElectionResult,
    ElectionResult,
)
from recommender.data.rcv.round_action import RoundAction
from recommender.db_config import DbSession
from recommender.rcv.election_update_stream import (
    ElectionResultEvent,
    ElectionUpdateStream,
)
from recommender.rcv.rcv_queue_config import rcv_vote_queue
from recommender.utilities.json_encode_utilities import NoNormalizationDict, json_encode

"""
Switch over to use messaging queues

Shard by election ID -- currently not done (OPTIONAL)
"""


class ElectionResultUpdateConsumer:
    QUEUE_NAME: Final[str] = rcv_vote_queue.name

    def consume(self, election_id: str):
        db_session = DbSession()
        rankings_by_voter: Dict[
            str, List[str]
        ] = Election.get_rankings_by_user_for_election(db_session, election_id)
        result = ElectionResult(self.__run_election(list(rankings_by_voter.values())))
        Election.update_election_by_id(
            db_session,
            election_id,
            {"election_result": result},
        )
        db_session.commit()
        ElectionUpdateStream.for_election(election_id).publish_message(
            ElectionResultEvent(DisplayableElectionResult.from_election_result(result))
        )

    def __run_election(
        self, rankings: List[List[str]]
    ) -> [Dict[str, CandidateRoundResult]]:
        total_votes = len(rankings)

        first_vote_counts = self.__count_first_ranks(rankings)
        vote_items = first_vote_counts.items()

        most_voted, most_first_one_votes = max(vote_items, key=lambda x: x[1])

        if most_first_one_votes > total_votes / 2:
            return [
                self.__get_candidate_round_results(
                    first_vote_counts, most_voted, RoundAction.WON
                )
            ]
        elif (
            most_first_one_votes == total_votes / 2
            and len(first_vote_counts.keys()) == 2
        ):
            return [
                self.__get_candidate_round_results(
                    first_vote_counts,
                    list(first_vote_counts.keys())[random.randrange(0, 2)],
                    candidate_round_action=RoundAction.WON_VIA_TIEBREAKER,
                )
            ]
        else:
            least_voted, least_first_one_votes = min(vote_items, key=lambda x: x[1])
            self.__eliminate_candidate(rankings, least_voted)
            return [
                self.__get_candidate_round_results(
                    first_vote_counts, least_voted, RoundAction.ELIMINATED
                )
            ] + self.__run_election(rankings=rankings)

    def __count_first_ranks(self, rankings: List[List[str]]) -> Counter:
        vote_counters = Counter({candidate: 0 for candidate in list(rankings[0])})
        for ranking in rankings:
            vote_counters[ranking[0]] += 1
        return vote_counters

    def __get_candidate_round_results(
        self,
        first_vote_counts: Dict[str, int],
        affected_candidate: str,
        candidate_round_action: RoundAction,
    ) -> Dict[str, CandidateRoundResult]:
        return {
            candidate_id: CandidateRoundResult(
                number_of_rank_one_votes=number_of_rank_one_votes_for_candidate,
                round_action=None
                if candidate_id != affected_candidate
                else candidate_round_action,
            )
            for candidate_id, number_of_rank_one_votes_for_candidate in first_vote_counts.items()
        }

    """
    Modifies rankings in-place
    """

    def __eliminate_candidate(self, rankings: List[List[str]], candidate_id: str):
        for ranking in rankings:
            ranking.remove(candidate_id)
