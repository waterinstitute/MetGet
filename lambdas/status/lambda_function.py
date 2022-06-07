#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2020 ADCIRC Development Group
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
def query_database():
    import pymysql
    import os
    import sys
    import json

    dbhost = os.environ["DBSERVER"]
    dbpassword = os.environ["DBPASS"]
    dbusername = os.environ["DBUSER"]
    dbname = "lambda_cache"

    try:
        db = pymysql.connect(
            host=dbhost,
            user=dbusername,
            passwd=dbpassword,
            db=dbname,
            connect_timeout=5,
        )
        cursor = db.cursor()
    except:
        print("[ERROR]: Could not connect to MySQL database")
        sys.exit(1)

    sql_query = "select json from status"
    cursor.execute(sql_query)
    query = cursor.fetchall()[0][0]

    return json.loads(query)


def lambda_handler(event, context):
    import uuid
    from datetime import datetime

    fn_start = datetime.now()
    rid = str(uuid.uuid4())

    data = query_database()

    return {
        "statusCode": 200,
        "body": {
            "message": "Data retrieved from the MetGet system",
            "version": "0.0.1",
            "request": rid,
            "response_time": ((datetime.now() - fn_start).total_seconds() * 1000.0),
            "accessed": str(datetime.now().isoformat()),
            "data": data,
        },
    }
