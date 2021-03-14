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
class Instance:

    def __init__(self):
        self.__instance_name = self.__get_instance_data("instanceId")
        self.__region = self.__get_instance_data("region")

    def region(self):
        return self.__region

    def name(self):
        return self.__instance_name

    def enable_termination_protection(self):
        self.__termination_protection(True)

    def disable_termination_protection(self):
        self.__termination_protection(False)
    
    def __termination_protection(self,value):
        import boto3
        ec2 = boto3.resource('ec2',region_name=self.__region)
        ec2.Instance(self.__instance_name).modify_attribute(DisableApiTermination={'Value': value})


    @staticmethod
    def __get_instance_data(key):
        import requests
        import json
        response = requests.get("http://169.254.169.254/latest/dynamic/instance-identity/document")
        data = json.loads(response.text)
        if key in data:
            return data[key]
        else:
            raise "Could not find key "+key+" in instance metadata"


