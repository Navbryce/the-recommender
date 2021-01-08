from rq import Queue

from recommender.db_config import primary_redis_conn

rcv_vote_queue = Queue(
    "rcv_election_result_update_queue", connection=primary_redis_conn
)
