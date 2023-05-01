from flask import make_response, Response


class AccessControl:
    """
    This class is used to check if the user is authorized to use the API
    """

    def __init__(self):
        """
        This method is used to initialize the class. It creates a database
        connection and a session object
        """
        from metget_api.metbuild.database import Database

        self.__db = Database()
        self.__session = self.__db.session()

    @staticmethod
    def hash_access_token(token: str) -> str:
        """
        This method is used to hash the access token before comparison
        """
        from hashlib import sha256

        return sha256(token.encode()).hexdigest()

    def is_authorized(self, api_key: str) -> bool:
        """
        This method is used to check if the user is authorized to use the API
        The method returns True if the user is authorized and False if not
        Keys are hashed before being compared to the database to prevent
        accidental exposure of the keys and/or sql injection
        """
        from metget_api.metbuild.tables import AuthTable

        api_key_hash = AccessControl.hash_access_token(str(api_key))
        api_key_db = (
            self.__session.query(AuthTable.id, AuthTable.key)
            .filter_by(key=api_key)
            .first()
        )

        if api_key_db == None:
            return False

        api_key_db_hash = AccessControl.hash_access_token(api_key_db.key.strip())

        if api_key_db_hash == api_key_hash:
            return True
        else:
            return False

    @staticmethod
    def check_authorization_token(headers) -> bool:
        """
        This method is used to check if the user is authorized to use the API
        The method returns True if the user is authorized and False if not
        """
        user_token = headers.get("x-api-key")
        gatekeeper = AccessControl()
        if gatekeeper.is_authorized(user_token):
            return True
        else:
            return False

    @staticmethod
    def unauthorized_response():
        status = 401
        return {"statusCode": status, "body": {"message": "ERROR: Unauthorized"}}, status
