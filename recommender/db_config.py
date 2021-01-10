import asyncio
import os

from redis import Redis
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from recommender.data.persistence_object import PersistenceObject
from recommender.env_config import PROD

engine = create_engine(
    "sqlite:///recommendation.db", connect_args={"check_same_thread": False}
)
if not PROD:

    @event.listens_for(engine, "connect")
    def activate_foreign_keys(connection, record):
        connection.execute("pragma foreign_keys=ON")


# engine = create_engine('mysql+mysqldb://root:mysql@localhost:3306/recommend', echo=True)
DbSession = sessionmaker(autoflush=True, bind=engine)
DbBase = declarative_base(cls=PersistenceObject)


def check_redis_connection(connection: Redis):
    connection.ping()


primary_redis_conn = Redis.from_url(os.environ["REDIS_URL"])
check_redis_connection(primary_redis_conn)
