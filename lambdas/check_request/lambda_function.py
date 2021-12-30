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
#
# Author: Zach Cobell
# Contact: zcobell@thewaterinstitute.org
#
def lambda_handler(event, context):
    import sys
    import pymysql
    from pymysql import MySQLError
    import boto3
    import os
    dbhost = os.environ["DBSERVER"]
    dbpassword = os.environ["DBPASS"]
    dbusername = os.environ["DBUSER"]
    dbname = os.environ["DBNAME"]
    bucket = os.environ["BUCKET_NAME"]
    try:
        db = pymysql.connect(host=dbhost,
                            user=dbusername,
                            passwd=dbpassword,
                            db=dbname,
                            connect_timeout=5)
        cursor = db.cursor()
    except MySQLError as e:
        return {
            'statusCode': 500,
            'body': {
                "status": "internal error",
                "message": "The system could not connect to the database"
            }
        }
        
    try: 
        request = event["request"]
        sql = "select * from requests where request_id = '"+request+"';"
        cursor.execute(sql)
        record = cursor.fetchone()
    
        if record:
            tries = record[2]
            status = record[3]
            message = record[4]
            start = record[5]
            last = record[6]
            destination = "https://"+bucket+".s3.amazonaws.com/" + request
            return {
                'statusCode': 200,
                'body': {
                    "status": status,
                    "message": message,
                    "tries": tries,
                    "start": str(start),
                    "last_update": str(last),
                    "destination": destination
                }
            } 

        else:
            return {
                'statusCode': 400,
                'body': {
                    "status": "error",
                    "message": "The requested record '"+request+"' was not found"
                }
            }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': {
                "status": "error",
                "error": "Could not process request, error was: "+str(e)
            }
        }

