class AccessControl:
    def __init__(self):
        from metget_api.database import Database

        self.__db = Database()
        self.__session = self.__db.session()

    def is_authorized(self, api_key: str) -> bool:
        from metget_api.tables import AuthTable

        return (
            self.__session.query(AuthTable.id)
            .filter_by(key=api_key, enabled=True)
            .first()
            is not None
        )

    @staticmethod
    def check_authorization_token(headers) -> bool:
        user_token = headers.get("x-api-key")
        gatekeeper = AccessControl()
        if gatekeeper.is_authorized(user_token):
            return True
        else:
            return False
