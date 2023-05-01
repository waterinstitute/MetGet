#!/usr/bin/env python3

from flask import Flask, redirect, request, make_response, jsonify
from flask_restful import Resource, Api
from flask_limiter import Limiter, RequestLimit
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from metget_api.access_control import AccessControl

application = Flask(__name__)
api = Api(application)
limiter = Limiter(
    get_remote_address,
    app=application,
    storage_uri="memory://",
)

CORS(application)


def ratelimit_error_responder(request_limit: RequestLimit):
    """
    This method is used to return a 429 error when the user has exceeded the
    rate limit

    Args:
        request_limit: The request limit object

    Returns:
        A 429 error response
    """
    return make_response(jsonify({"error": "rate_limit_exceeded"}), 429)


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
        model: Name of the meteorolgoical model to return. Default is 'all'
        limit: Maximum number of days worth of data to return. Default is 7
    """

    decorators = [limiter.limit("10/second", on_breach=ratelimit_error_responder)]

    @staticmethod
    def get():
        """
        This method is used to check the status of the MetGet API and see what
        data is currently available in the database
        """
        authorized = AccessControl.check_authorization_token(request.headers)
        if authorized:
            return MetGetStatus.__get_status()
        else:
            return AccessControl.unauthorized_response()

    @staticmethod
    def __get_status():
        """
        This method is used to check the status of the MetGet API and see what
        data is currently available in the database
        """
        from metget_api.status import Status
        from datetime import timedelta

        if "model" in request.args:
            model = request.args["model"]
        else:
            model = "all"

        if "limit" in request.args:
            limit_days = request.args["limit"]
            try:
                limit_days_int = int(limit_days)
            except ValueError as v:
                return {
                    "statusCode": 400,
                    "body": {"message": "ERROR: Invalid limit specified"},
                }, 400
        else:
            limit_days_int = 7

        time_limit = timedelta(days=limit_days_int)

        s = Status()
        status_data, status_code = s.get_status(model, time_limit)
        return {"statusCode": status_code, "body": status_data}, status_code


class MetGetBuild(Resource):
    """
    This class is used to build a new MetGet request into a 2d wind field

    This is found at the /build path
    """

    decorators = [limiter.limit("10/second", on_breach=ratelimit_error_responder)]

    @staticmethod
    def post():
        """
        This method is used to build a new MetGet request into a 2d wind field
        """
        authorized = AccessControl.check_authorization_token(request.headers)
        if authorized:
            return MetGetBuild.__build()
        else:
            return AccessControl.unauthorized_response()

    @staticmethod
    def __build():
        """
        This method is used to build a new MetGet request into a 2d wind field
        """
        import uuid

        from metget_api.metbuildrequest import MetBuildRequest

        request_uuid = str(uuid.uuid4())
        request_api_key = request.headers.get("x-api-key")
        request_source_ip = request.remote_addr
        request_json = request.get_json()

        request_json["source-ip"] = request_source_ip

        request_obj = MetBuildRequest(
            request_api_key, request_source_ip, request_uuid, request_json
        )
        message, status_code = request_obj.generate_request()

        return message, status_code


class MetGetCheckRequest(Resource):
    """
    Allows users to check on the status of a request that is currently being built

    The request is specified as a query string parameter "request-id" to the get method
    """

    decorators = [limiter.limit("10/second", on_breach=ratelimit_error_responder)]

    def get(self):
        authorized = AccessControl.check_authorization_token(request.headers)
        if authorized:
            return self.__get_request_status()
        else:
            return AccessControl.unauthorized_response()

    def __get_request_status(self):
        from metbuild.database import Database
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

        db = Database()
        session = db.session()

        query_result = (
            session.query(
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
            bucket_name = os.environ["METGET_S3_BUCKET"]
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


class MetGetTrack(Resource):
    """
    Allows users to query a storm track in geojson format from the MetGet database

    The endpoint takes the following query parameters:
        - advisory - The nhc advisory number
        - basin - The nhc basin (i.e. al, wp)
        - storm - The nhc storm number
        - type - Type of track to return (best or forecast)
        - year - The year that the storm occurs

    """

    decorators = [limiter.limit("10/second", on_breach=ratelimit_error_responder)]

    def get(self):
        # authorized = AccessControl.check_authorization_token(request.headers)
        # if authorized:
        #    return self.__get_storm_track()
        # else:
        #    return AccessControl.unauthorized_response()
        # ...We currently have the stormtrack endpoint without authorization so that
        # web portals can use freely. One day it can be locked up if desired using
        # the above
        return self.__get_storm_track()

    def __get_storm_track(self):
        from metget_api.database import Database
        from metget_api.tables import NhcBtkTable, NhcFcstTable

        advisory = None
        basin = None
        storm = None
        year = None
        track_type = None

        if "type" in request.args:
            track_type = request.args["type"]
            if track_type != "best" and track_type != "forecast":
                return {
                    "statusCode": 400,
                    "body": {
                        "message": "ERROR: Invalid track type specified: {:s}".format(
                            track_type
                        )
                    },
                }, 400
        else:
            return {
                "statusCode": 400,
                "body": {
                    "message": "ERROR: Query string parameter 'type' not provided"
                },
            }, 400

        if track_type == "forecast":
            if "advisory" in request.args:
                advisory = request.args["advisory"]
            else:
                return {
                    "statusCode": 400,
                    "body": {
                        "message": "ERROR: Query string parameter 'advisory' not provided"
                    },
                }, 400

        if "basin" in request.args:
            basin = request.args["basin"]
        else:
            return {
                "statusCode": 400,
                "body": {
                    "message": "ERROR: Query string parameter 'basin' not provided"
                },
            }, 400

        if "storm" in request.args:
            storm = request.args["storm"]
        else:
            return {
                "statusCode": 400,
                "body": {
                    "message": "ERROR: Query string parameter 'storm' not provided"
                },
            }, 400

        if "year" in request.args:
            year = request.args["year"]
        else:
            return {
                "statusCode": 400,
                "body": {
                    "message": "ERROR: Query string parameter 'year' not provided"
                },
            }, 400

        db = Database()
        session = db.session()

        if track_type == "forecast":
            query_result = (
                session.query(NhcFcstTable.geometry_data)
                .filter(
                    NhcFcstTable.storm_year == year,
                    NhcFcstTable.basin == basin,
                    NhcFcstTable.storm == storm,
                    NhcFcstTable.advisory == advisory,
                )
                .all()
            )
        else:
            query_result = (
                session.query(NhcBtkTable.geometry_data)
                .filter(
                    NhcBtkTable.storm_year == year,
                    NhcBtkTable.basin == basin,
                    NhcBtkTable.storm == storm,
                )
                .all()
            )

        if len(query_result) == 0:
            return {
                "statusCode": 400,
                "body": "ERROR: No data found to match request",
            }, 400
        elif len(query_result) > 1:
            return {
                "statusCode": 400,
                "body": "ERROR: Too many records found matching request",
            }, 400
        else:
            return {"statusCode": 200, "body": {"geojson": query_result[0][0]}}, 200


# ...Add the resources to the API
api.add_resource(MetGetStatus, "/status")
api.add_resource(MetGetBuild, "/build")
api.add_resource(MetGetCheckRequest, "/check")
api.add_resource(MetGetTrack, "/stormtrack")

if __name__ == "__main__":
    """
    If the script is run directly, start the application server
    using flask's built-in server. This is for testing purposes
    only and should not be used in production.
    """
    application.run(host="0.0.0.0", port=5000)
