from typing import Tuple


class MetBuildRequest:
    """
    This class is used to build a new MetGet request into a 2d wind field
    """

    def __init__(self, api_key: str, source_ip: str, request_id: str, json_data: dict):
        """
        Constructor for BuildRequest

        Args:
            request_id: A string containing the request id
            api_key: A string containing the api key
            source_ip: A string containing the source ip
            json_data: A dictionary containing the json data for the request
        """
        import os

        self.__json_data = json_data
        self.__api_key = api_key
        self.__source_ip = source_ip
        self.__request_id = request_id
        self.__output_bucket = os.environ["METGET_S3_BUCKET_UPLOAD"]
        self.__build_request = None
        self.__error = []

    def generate_request(self) -> Tuple[dict, int]:
        """
        This method is used to add a new request to the database and initiate
        the k8s process within argo

        Returns:
            A tuple containing the response message and status code
        """
        from metget_api.build_request import BuildRequest
        from metbuild.tables import RequestEnum

        self.__build_request = BuildRequest(
            self.__request_id, self.__api_key, self.__source_ip, self.__json_data, True
        )

        statuscode = 200
        msg = {
            "statusCode": 200,
            "body": {
                "status": "empty",
                "message": "empty",
                "request_id": "empty",
                "request_url": "empty",
                "error_text": [],
            },
        }

        valid = self.__build_request.validate()
        if valid:
            if self.__build_request.input_obj().dry_run():
                msg["body"]["status"] = "success"
                msg["body"]["message"] = "dry run successful"
                msg["body"]["request_id"] = self.__build_request.request_id()
                msg["body"]["request_url"] = "n/a"
                msg["body"]["error_text"] = []
            else:
                msg["body"]["status"] = "success"
                msg["body"]["message"] = "Request added to queue"
                msg["body"]["request_id"] = self.__build_request.request_id()
                msg["body"][
                    "request_url"
                ] = "https://{:s}.s3.amazonaws.com/{:s}".format(
                    self.__output_bucket, self.__build_request.request_id()
                )
                msg["body"]["error_text"] = []

                self.__build_request.add_request(
                    RequestEnum.queued, "Request added to queue", True
                )

        else:
            statuscode = 401
            msg["statusCode"] = 401
            msg["body"]["status"] = "error"
            msg["body"]["message"] = "Request could not be added to queue"
            msg["body"]["request_id"] = self.__build_request.request_id()
            msg["body"]["request_url"] = "n/a"
            msg["body"]["error_text"] = self.__build_request.error()

        return msg, statuscode
