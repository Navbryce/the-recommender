"""
Switch over to use messaging queues

Shard by election ID -- currently not done (OPTIONAL)
"""
from typing import Final

from recommender.rcv.rcv_queue_config import rcv_vote_queue


class ElectionResultUpdateConsumer:
    QUEUE_NAME: Final[str] = rcv_vote_queue.name

    def consume(self, election_id: str):
        print(f"Sync for {election_id}")
