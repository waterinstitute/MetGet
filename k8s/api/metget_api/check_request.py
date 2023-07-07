#!/usr/bin/env python3
###################################################################################################
# MIT License
#
# Copyright (c) 2023 The Water Institute
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Author: Zach Cobell
# Contact: zcobell@thewaterinstitute.org
# Organization: The Water Institute
#
###################################################################################################
from typing import Tuple


class CheckRequest:
    def __init__(self):
        pass

    def get(self, request) -> Tuple[dict, int]:
        """
        This method is used to check the status of a MetGet request

        Args:
            request: A flask request object

        Returns:
            A tuple containing the response message and status code
        """
        from metbuild.tables import RequestTable
        from metbuild.database import Database

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

        with Database() as db, db.session() as session:
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
