from tables import RequestTable, RequestEnum


class BuildRequest:
    """
    This class is used to build a new MetGet request into a 2d wind field
    and initiate the k8s process within argo
    """

    def __init__(self):
        """
        Constructor
        """
        from database import Database

        self.__db = Database()
        self.__session = self.__db.session()

    def add_request(
        self,
        request_id: str,
        request_status: RequestEnum,
        try_count: int,
        api_key: str,
        source_ip: str,
        request_json: dict,
    ) -> None:
        """
        This method is used to add a new request to the database and initiate
        the k8s process within argo
        """
        from datetime import datetime

        record = RequestTable(
            request_id=request_id,
            try_count=try_count,
            status=request_status,
            start_date=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            last_date=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            api_key=api_key,
            source_ip=source_ip,
            input_data=request_json,
        )

        qry_object = self.__session.query(RequestTable).where(
            RequestTable.request_id == record.request_id
        )
        if qry_object.first() is None:
            self.__session.add(record)

        self.__session.commit()

    def update_request(
        self,
        request_id: str,
        request_status: RequestEnum,
        try_count: int,
    ) -> None:
        """
        This method is used to update a request in the database that has
        begun processing
        """
        from datetime import datetime

        qry_object = self.__session.query(RequestTable).where(
            RequestTable.request_id == request_id
        )
        if qry_object.first() is not None:
            qry_object.update(
                {
                    RequestTable.try_count: try_count,
                    RequestTable.status: request_status,
                    RequestTable.last_date: datetime.utcnow().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                }
            )

        self.__session.commit()
