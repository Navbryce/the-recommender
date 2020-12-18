from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///recommendation.db")
# engine = create_engine('mysql+mysqldb://root:mysql@localhost:3306/recommend', echo=True)
DbSession = sessionmaker(autoflush=True, bind=engine)
DbBase = declarative_base()
