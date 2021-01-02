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
