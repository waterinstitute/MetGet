from metget_api.tables import RequestTable, RequestEnum


class Request:
    def __init__(self):
        from metget_api.database import Database

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
        from sqlalchemy import insert
        from datetime import datetime

        record = RequestTable(
            request_id=request_id,
            try_count=0,
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
