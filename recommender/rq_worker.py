import os

from dotenv import load_dotenv
from rq import Connection, Queue

from recommender.env_config import HEROKU

load_dotenv(verbose=True)

from recommender.db_config import primary_redis_conn


# import correct worker
if HEROKU:
    from rq.worker import HerokuWorker as Worker
else:
    from rq.worker import Worker

# optimization -> Import all libraries used in the consumer function
from recommender.rcv.election_result_update_consumer import ElectionResultUpdateConsumer

QUEUES_TO_WORK = [ElectionResultUpdateConsumer.QUEUE_NAME]

if __name__ == "__main__":
    with Connection(primary_redis_conn):
        worker = Worker(map(Queue, QUEUES_TO_WORK))
        worker.work()
