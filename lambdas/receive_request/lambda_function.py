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
def queue_name():
    import os
    return os.environ["QUEUE_NAME"]


def region():
    import os
    return os.environ["AWS_REGION"]


def count_forecasts(grib_list):
    dates = set()
    for file in grib_list:
        dates.add(file[2])
    return len(dates)


def check_time_step(grib_list):
    dt = []
    for i in range(len(grib_list) - 1):
        dt.append((grib_list[i + 1][0] - grib_list[i][0]).seconds)
    return dt


def check_forecast_hours(grib_list):
    dt = []
    for f in grib_list:
        cycle = f[2]
        date = f[0]
        dt.append((date - cycle).seconds)
    return dt


def validate(json_data):
    from metbuild.database import Database
    from metbuild.input import Input

    input_data = Input(json_data, None, None, None, True)
    error = []

    # ... Step 1: Check if we can even parse something reasonable from the JSON
    if not input_data.valid():
        error.append(input_data.error())
        return False, error

    # ... Step 2: Check if the options can be fulfilled
    db = Database()
    for i in range(input_data.num_domains()):
        d = input_data.domain(i)
        lookup = db.generate_file_list(d.service(), input_data.start_date(), input_data.end_date(), d.storm(),
                                       input_data.nowcast(), input_data.multiple_forecasts())
                                       
        if len(lookup)<2:
            error.append("Insufficient data was available for domain "+str(i))
            return False, error
            if input_data.strict():
                return False, error
            continue
                                       
        n_forecasts = count_forecasts(lookup)
        dt = check_time_step(lookup)
        forecast_hours = check_forecast_hours(lookup)
        start_data_time = lookup[0][0]
        end_data_time = lookup[-1][0]

        if input_data.start_date() < start_data_time:
            error.append("Specified start date is before the beginning of available data, domain " + str(i))
            if input_data.strict():
                return False, error
        if input_data.end_date() > end_data_time:
            error.append("Specified end date is after the end of available data, domain " + str(i))
            if input_data.strict():
                return False, error

        if not input_data.multiple_forecasts():
            if n_forecasts > 1:
                error.append("Did not satisfy request for a single forecast, domain " + str(i))
                if not input_data.strict():
                    return False, error
        elif input_data.nowcast():
            for d in forecast_hours:
                if not d == 0:
                    error.append("Did not generate a 6-hour nowcast, domain " + str(i))
                    if not input_data.strict():
                        return False, error
                    break

    return True, error


def lambda_handler(event, context):
    import json
    import boto3
    import logging
    from metbuild.database import Database
    from metbuild.input import Input

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    json_request = event["body-json"]
    json_request["api-key"] = event["context"]["api-key"]
    json_request["source-ip"] = event["context"]["source-ip"]
    
    valid, error = validate(json_request)

    if valid:
        
        input_data = Input(json_request, None, None, None, True)
        
        msg = None
        status = 500

        try:
            if input_data.dry_run():
                msg = {"MessageId": "DRY-RUN"}
                status = 200
            else:
                client = boto3.client('sqs', region_name=region())
                queue_url = client.get_queue_url(QueueName=queue_name())['QueueUrl']
                db = Database()
                msg = client.send_message(QueueUrl=queue_url, MessageBody=json.dumps(json_request))
                db.add_request_to_queue(msg["MessageId"], json_request)
                status = 200
        except Exception as e:
            error_message = str(e)
            logger.error("Could not send the message to the queue. Message has been rejected")
            status = 500

        if status == 200:
            return {
                'statusCode': 200,
                'body': {
                    "status": "success",
                    "message": "Message received and added to queue",
                    "request_id": msg["MessageId"],
                    "request_url": "https://metget-output.s3.amazonaws.com/" + msg["MessageId"],
                    "error_text": "n/a"
                }
            }
        else:
            return {
                'statusCode': 500,
                'body': {
                    "status": "error",
                    "message": "Message could not be added to the queue, system error",
                    "request_id": "n/a",
                    "request_url": "n/a",
                    "error_text": error_message
                }
            }
    else:
        return {
            'statusCode': 400,
            'body': {
                "status": "error",
                "message": "Input data contained an error",
                "request_id": "n/a",
                "request_url": "n/a",
                "error_text": error
            }
        }


