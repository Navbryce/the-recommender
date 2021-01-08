import os

from redis import Redis
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from recommender.data.persistence_object import PersistenceObject

engine = create_engine(
    "sqlite:///recommendation.db", connect_args={"check_same_thread": False}
)
# engine = create_engine('mysql+mysqldb://root:mysql@localhost:3306/recommend', echo=True)
DbSession = sessionmaker(autoflush=True, bind=engine)
DbBase = declarative_base(cls=PersistenceObject)

primary_redis_conn = Redis(
    os.environ["REDIS_HOST"],
    os.environ["REDIS_PORT"],
    password=None if "REDIS_PASS" not in os.environ else os.environ["REDIS_PASS"],
)
