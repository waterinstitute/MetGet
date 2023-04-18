#!/usr/bin/env python3

from flask import Flask, redirect, request
from metget_api.access_control import AccessControl
from flask_restful import Resource, Api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

application = Flask(__name__)
api = Api(application)
limiter = Limiter(
    get_remote_address,
    app=application,
    storage_uri="memory://",
)

@application.route("/")
def index():
    """
    When the user hits the root path, redirect them to the MetGet homepage
    """
    return redirect(location="http://metget.org", code=302)


class MetGetStatus(Resource):
    """
    This class is used to check the status of the MetGet API and see what
    data is currently available in the database

    This is found at the /status path

    It may take url query arguments of:
        model: Name of the meteorolgoical model to return. Default is 'gfs'
        limit: Maximum number of days worth of data to return. Default is 31
    """

    decorators = [limiter.limit("10/second")]

    def get(self):
        """
        This method is used to check the status of the MetGet API and see what
        data is currently available in the database
        """
        authorized = AccessControl.check_authorization_token(request.headers)
        if authorized:
            return self.__get_status()
        else:
            return {"message": "ERROR: Unauthorized"}, 401

    def __get_status(self):
        """
        This method is used to check the status of the MetGet API and see what
        data is currently available in the database
        """
        from metget_api.status import Status
        import json
        from datetime import timedelta

        if "model" in request.args:
            model = request.args["model"]
        else:
            model = "gfs"

        if "limit" in request.args:
            limit_days = request.args["limit"]
            try:
                limit_days_int = int(limit_days)
            except ValueError as v:
                return {"message": "ERROR: Invalid limit specified"}, 401
        else:
            limit_days_int = 7

        time_limit = timedelta(days=limit_days_int)

        s = Status()
        status_data, status_code = s.get_status(model, time_limit)
        return status_data, status_code


class MetGetBuild(Resource):
    """
    This class is used to build a new MetGet request into a 2d wind field

    This is found at the /build path
    """
    
    decorators = [limiter.limit("10/second")]

    def post(self):
        """
        This method is used to build a new MetGet request into a 2d wind field
        """
        authorized = AccessControl.check_authorization_token(request.headers)
        if authorized:
            return self.__build()
        else:
            return {"message": "ERROR: Unauthorized"}, 401

    def __build(self):
        """
        This method is used to build a new MetGet request into a 2d wind field
        """
        import uuid

        from metget_api.build_request import BuildRequest
        from metget_api.tables import RequestEnum

        request_uuid = str(uuid.uuid4())
        request_api_key = request.headers.get("x-api-key")
        request_source_ip = request.remote_addr
        request_json = request.get_json()

        request_json["source-ip"] = request_source_ip

        request_obj = BuildRequest()
        request_obj.add_request(
            request_uuid,
            RequestEnum.queued,
            0,
            request_api_key,
            request_source_ip,
            request_json,
        )

        return {"message": "Success", "request-id": request_uuid}, 200


# ...Add the resources to the API
api.add_resource(MetGetStatus, "/status")
api.add_resource(MetGetBuild, "/build")

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5000)
