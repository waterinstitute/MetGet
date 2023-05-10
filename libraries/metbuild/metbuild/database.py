class Database:
    """
    Database class for interacting with the database
    """

    def __init__(self):
        """
        Constructor for Database class

        Initialize the database engine and session
        """
        from sqlalchemy.orm import Session

        self.__engine = self.__init_database_engine()
        self.__session = Session(self.__engine)

    def __enter__(self):
        """
        Enter method for Database class for use with context managers
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit method for Database class for use with context managers. Note that
        this method will rollback any uncommitted transactions and close the
        database connection. This method will also dispose of the database
        engine. This assumes that anything the user wants, they will
        have already committed to the database.
        """
        self.__session.rollback()
        self.__session.close()
        self.__engine.dispose()

    def __del__(self):
        """
        Destructor for Database class. Note that this method will rollback any
        uncommitted transactions and close the database connection. This method
        will also dispose of the database engine. This assumes that anything
        the user wants, they will have already committed to the database.
        """
        self.__session.rollback()
        self.__session.close()
        self.__engine.dispose()

    def session(self):
        """
        Return the database session
        """
        return self.__session

    @staticmethod
    def __init_database_engine():
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
        return create_engine(url, isolation_level="REPEATABLE_READ", pool_pre_ping=True)
