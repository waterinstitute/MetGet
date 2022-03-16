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

class Queue:
    def __init__(self,log):
        from .instance import Instance
        inst = Instance()
        self.__queue_name = self.__get_queue_name()
        self.__client = boto3.client('sqs',region_name=inst.region())
        self.__url = self.__client.get_queue_url(QueueName=self.queue_name())['QueueUrl']
        self.__log = log

    def queue_name(self):
        return self.__queue_name

    def url(self):
        return self.__url

    @staticmethod
    def __get_queue_name():
        import os
        return os.environ["QUEUE_NAME"]
    
    # Gets the next message from the SQS 
    def get_next_message(self):
        response = self.__client.receive_message(QueueUrl=self.url(),MaxNumberOfMessages=1,WaitTimeSeconds=1)
        if "Messages" in response:
            msg = response["Messages"][0]
            self.hold_message(msg["ReceiptHandle"])
            return True,msg
        else:
            return False,""
    
    # Deletes the specified message from the SQS once the job is complete
    def delete_message(self,message_id):
        response = self.__client.delete_message(QueueUrl=self.url(),ReceiptHandle=message_id)

    def hold_message(self,message_id):
        response = self.__client.change_message_visibility(QueueUrl=self.url(), ReceiptHandle=message_id, VisibilityTimeout=7200)

    def release_message(self,message_id):
        response = self.__client.change_message_visibility(QueueUrl=self.url(), ReceiptHandle=message_id, VisibilityTimeout=120)
