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

import boto3
import botocore
from botocore.exceptions import ClientError


class S3file:
    def __init__(self):
        import os

        self.__bucket = os.environ["METGET_S3_BUCKET"]
        self.__client = boto3.client("s3")
        self.__resource = boto3.resource("s3")

    def upload_file(self, local_file, remote_path):
        """Upload a file to an S3 bucket
        :param local_file: local path to file for upload
        :param remote_path: desired path to the remote file
        :return: True if file was uploaded, else False
        """
        import logging

        logger = logging.getLogger(__name__)
        # Upload the file
        try:
            response = self.__client.upload_file(
                local_file,
                self.__bucket,
                remote_path,
                ExtraArgs={"StorageClass": "INTELLIGENT_TIERING"},
            )
        except ClientError as e:
            logger.error(str(e))
            return False

        return True

    def download_file(self, remote_path, local_path):
        import logging

        logger = logging.getLogger(__name__)
        try:
            response = self.__client.download_file(
                self.__bucket, remote_path, local_path
            )
        except ClientError as e:
            logger.error(str(e))
            return False
        return True

    def exists(self, path):
        import logging

        logger = logging.getLogger(__name__)
        try:
            self.__resource.Object(self.__bucket, path).load()
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            else:
                # Something else has gone wrong.
                logger.error(str(e))
                raise
        return True
