def __init_database():
    """
    Initialize the database engine and return it.
    """
    import os
    from sqlalchemy import create_engine, URL

    db_host = os.environ["METGET_DATABASE_SERVICE_HOST"]
    db_password = os.environ["METGET_DATABASE_PASSWORD"]
    db_username = os.environ["METGET_DATABASE_USER"]
    db_name = os.environ["METGET_DATABASE"]
    url = URL.create(
        "postgresql+psycopg2",
        username=db_username,
        password=db_password,
        host=db_host,
        database=db_name,
    )
    return create_engine(
        url, isolation_level="REPEATABLE_READ", pool_pre_ping=True, pool_size=20
    )


# Initialize the database engine and store it in a global variable.
DATABASE_ENGINE = __init_database()


class Database:
    """
    A class to manage the database connection.
    """

    def __init__(self):
        """
        Initialize the database session
        """
        self.__session = None
        self.__connect()

    def __connect(self):
        """
        Connect to the database and generate a session.
        """
        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=DATABASE_ENGINE)
        self.__session = Session()

    def session(self):
        """
        Return the database session.
        """
        return self.__session
