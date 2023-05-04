from typing import Tuple


class CheckRequest:
    def __init__(self):
        """
        Constructor for CheckRequest class
        """
        from metbuild.database import Database

        self.__db = Database()
        self.__session = self.__db.session()

    def get(self, request) -> Tuple[dict, int]:
        """
        This method is used to check the status of a MetGet request

        Args:
            request: A flask request object

        Returns:
            A tuple containing the response message and status code
        """
        from metbuild.tables import RequestTable
        import os

        if "request-id" in request.args:
            request_id = request.args["request-id"]
        else:
            return {
                "statusCode": 400,
                "body": {
                    "message": "ERROR: Query string parameter 'request-id' not found"
                },
            }, 400

        query_result = (
            self.__session.query(
                RequestTable.try_count,
                RequestTable.status,
                RequestTable.start_date,
                RequestTable.last_date,
                RequestTable.message,
            )
            .filter(RequestTable.request_id == request_id)
            .all()
        )

        if len(query_result) == 0:
            return {
                "statusCode": 400,
                "body": {
                    "message": "ERROR: Request '{:s}' was not found".format(request_id)
                },
            }, 400
        elif len(query_result) > 1:
            return {
                "statusCode": 400,
                "body": {
                    "message": "ERROR: Request '{:s}' is ambiguous".format(request_id)
                },
            }, 400
        else:
            row = query_result[0]
            bucket_name = os.environ["METGET_S3_BUCKET_UPLOAD"]
            upload_destination = "https://{:s}.s3.amazonaws.com/{:s}".format(
                bucket_name, request_id
            )
            return {
                "statusCode": 200,
                "body": {
                    "request-id": request_id,
                    "status": row[1].name,
                    "message": row[4],
                    "try_count": row[0],
                    "start": row[2].strftime("%Y-%m-%d %H:%M:%S"),
                    "last_update": row[3].strftime("%Y-%m-%d %H:%M:%S"),
                    "destination": upload_destination,
                },
            }, 200
