class Database:
    def __init__(self):
        import os

        self.__dbhost = os.environ["METGET_DATABASE_SERVICE_HOST"]
        self.__dbpassword = os.environ["METGET_DATABASE_PASSWORD"]
        self.__dbusername = os.environ["METGET_DATABASE_USER"]
        self.__dbname = os.environ["METGET_DATABASE"]
        self.__engine = None
        self.__session = None
        self.__connect()

    def __connect(self):
        from sqlalchemy import create_engine, URL
        from sqlalchemy.orm import sessionmaker

        url = URL.create(
            "postgresql+psycopg2",
            username=self.__dbusername,
            password=self.__dbpassword,
            host=self.__dbhost,
            database=self.__dbname,
        )
        self.__engine = create_engine(
            url, isolation_level="REPEATABLE_READ", pool_pre_ping=True
        )
        Session = sessionmaker(bind=self.__engine)
        self.__session = Session()

    def engine(self):
        return self.__engine

    def session(self):
        return self.__session
