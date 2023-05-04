

def __init_database():
    import os
    from sqlalchemy import create_engine, URL
    dbhost = os.environ["METGET_DATABASE_SERVICE_HOST"]
    dbpassword = os.environ["METGET_DATABASE_PASSWORD"]
    dbusername = os.environ["METGET_DATABASE_USER"]
    dbname = os.environ["METGET_DATABASE"]
    url = URL.create(
        "postgresql+psycopg2",
        username=dbusername,
        password=dbpassword,
        host=dbhost,
        database=dbname,
    )
    return create_engine(
        url, isolation_level="REPEATABLE_READ", pool_pre_ping=True, pool_size=20
    )

DATABASE_ENGINE = __init_database()

class Database:
    def __init__(self):
        self.__session = None
        self.__connect()

    def __connect(self):
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=DATABASE_ENGINE)
        self.__session = Session()

    def session(self):
        return self.__session
