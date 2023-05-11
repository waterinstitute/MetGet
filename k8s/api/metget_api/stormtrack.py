from typing import Tuple


class StormTrack:
    """
    This class is used to query the NHC storm track data from MetGet
    """

    def __init__(self):
        """
        Constructor for StormTrack class
        """
        pass

    def get(self, request) -> Tuple[dict, int]:
        """
        This method is used to query the NHC storm track data from MetGet

        Args:
            request: A flask request object

        Returns:
            A tuple containing the response message and status code
        """

        from metbuild.tables import NhcBtkTable, NhcFcstTable
        from metbuild.database import Database

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
                advisory_str = request.args["advisory"]
                try:
                    advisory_int = int(advisory_str)
                    advisory = "{:03d}".format(advisory_int)
                except ValueError:
                    advisory = advisory_str
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

        with Database() as db, db.session() as session:
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
