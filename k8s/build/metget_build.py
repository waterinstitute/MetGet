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

import logging
import os
from datetime import datetime, timedelta

from metbuild.tables import RequestTable
from message_handler import MessageHandler

MAX_REQUEST_TIME = timedelta(hours=48)
REQUEST_SLEEP_TIME = timedelta(minutes=10)


def main():
    """
    Main entry point for the script
    """
    import json
    import time
    import traceback

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s :: %(levelname)s :: %(filename)s :: %(funcName)s :: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%Z",
    )

    log = logging.getLogger(__name__)
    log.info("Beginning execution")

    try:
        # ...Get the input data from the environment.
        # This variable is set by the argo template
        # and comes from rabbitmq
        message = os.environ["METGET_REQUEST_JSON"]
        json_data = json.loads(message)

        credit_cost = 0

        handler = MessageHandler(json_data)
        credit_cost = handler.input().credit_usage()

        RequestTable.update_request(
            json_data["request_id"],
            "running",
            json_data["api_key"],
            json_data["source_ip"],
            json_data,
            "Job is running",
            credit_cost,
        )

        status = False

        start_time = datetime.now()

        #  Process the message. This will return True if the job is complete
        #  or False if the job is not complete. If the job is not complete,
        #  it will sleep for REQUEST_SLEEP_TIME seconds and then check again.
        #  If the job is not complete after MAX_REQUEST_TIME seconds, it will
        #  raise a RuntimeError
        while status is False:
            status = handler.process_message()

            if datetime.now() - start_time > MAX_REQUEST_TIME:
                raise RuntimeError("Job exceeded maximum run time of 48 hours")

            if status is False:
                time.sleep(REQUEST_SLEEP_TIME.total_seconds())

        RequestTable.update_request(
            json_data["request_id"],
            "completed",
            json_data["api_key"],
            json_data["source_ip"],
            json_data,
            "Job completed successfully",
            credit_cost,
        )
    except RuntimeError as e:
        log.error("Encountered error during processing: " + str(e))
        log.error(traceback.format_exc())
        RequestTable.update_request(
            json_data["request_id"],
            "error",
            json_data["api_key"],
            json_data["source_ip"],
            json_data,
            "Job encountered an error: {:s}".format(str(e)),
            credit_cost,
        )
    except KeyError as e:
        log.error("Encountered malformed json input: " + str(e))
        log.error(traceback.format_exc())
        RequestTable.update_request(
            json_data["request_id"],
            "error",
            json_data["api_key"],
            json_data["source_ip"],
            json_data,
            "Job encountered an error: {:s}".format(str(e)),
            credit_cost,
        )
    except Exception as e:
        log.error("Encountered unexpected error: " + str(e))
        log.error(traceback.format_exc())
        RequestTable.update_request(
            json_data["request_id"],
            "error",
            json_data["api_key"],
            json_data["source_ip"],
            json_data,
            "Job encountered an unhandled error: {:s}".format(str(e)),
            credit_cost,
        )
        raise

    log.info("Exiting script with status 0")
    exit(0)


if __name__ == "__main__":
    main()
