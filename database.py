from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


URL_CONNECTION = 'mysql+pymysql://juanda:123456@localhost:3310/test'


engine = create_engine(URL_CONNECTION)

localSession = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()