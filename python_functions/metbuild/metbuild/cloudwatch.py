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
import boto3


class CloudWatch:
    def __init__(self):
        from .instance import Instance
        from datetime import datetime

        inst = Instance()
        self.__region = inst.region()
        self.__client = boto3.client("logs", region_name=self.__region)
        self.__instance = inst.name()
        self.__logGroup = "metget-stack01-loggroup"
        self.__logStream = "metbuild_log_" + self.__instance
        self.__epoch = datetime(1970, 1, 1, 0, 0, 0)

        response = self.__client.describe_log_streams(
            logGroupName=self.__logGroup, logStreamNamePrefix=self.__logStream
        )
        if len(response["logStreams"]) == 0:
            self.__client.create_log_stream(
                logGroupName=self.__logGroup, logStreamName=self.__logStream
            )

    def __get_sequence_token(self):
        response = self.__client.describe_log_streams(
            logGroupName=self.__logGroup, logStreamNamePrefix=self.__logStream
        )
        if len(response["logStreams"]) > 0:
            if "uploadSequenceToken" in response["logStreams"][0]:
                return response["logStreams"][0]["uploadSequenceToken"]
        return None

    def __log(self, level, message):
        from datetime import datetime
        import json

        event = [
            {
                "timestamp": int(
                    (datetime.utcnow() - self.__epoch).total_seconds() * 1000
                ),
                "message": json.dumps(
                    {"instance": self.__instance, "level": level, "body": message}
                ),
            }
        ]
        for i in range(20):
            try:
                token = self.__get_sequence_token()
                if token:
                    response = self.__client.put_log_events(
                        logGroupName=self.__logGroup,
                        logStreamName=self.__logStream,
                        logEvents=event,
                        sequenceToken=token,
                    )
                else:
                    response = self.__client.put_log_events(
                        logGroupName=self.__logGroup,
                        logStreamName=self.__logStream,
                        logEvents=event,
                    )
                break
            except:
                continue

    def info(self, message):
        self.__log("INFO", message)

    def error(self, message):
        self.__log("ERROR", message)

    def warning(self, message):
        self.__log("WARNING", message)

    def debug(self, message):
        self.__log("DEBUG", message)
