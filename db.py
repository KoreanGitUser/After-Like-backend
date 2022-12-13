# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

#user_name = "root"
#user_pwd = "123457"
#db_host = "localhost"
#db_name = "test"

DATABASE = "mysql+pymysql://inho:k123456789@project-db-stu.ddns.net:3307/inho?charset=utf8mb4"


ENGINE = create_engine(
    DATABASE,
    encoding="utf-8",
    echo=True
)

session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=ENGINE
    )
)

Base = declarative_base()
# Base.query = session.query_property()
