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

from metbuild.cloudwatch import CloudWatch
logger = CloudWatch()

# Function to genreate a date range
def datespan(startDate, endDate, delta):
    from datetime import datetime,timedelta
    currentDate = startDate
    while currentDate <= endDate:
        yield currentDate
        currentDate += delta

# Main function to process the message and create the output files and post to S3
def process_message(json_message, queue, json_file=None):
    import time
    import json
    import pymetbuild
    import datetime
    import os
    import json
    from metbuild.instance import Instance
    from metbuild.input import Input
    from metbuild.database import Database
    from metbuild.s3file import S3file

    filelist_name = "filelist.json"

    instance = Instance()

    instance.enable_termination_protection()

    if json_file:
        logger.info("Processing message from file: "+json_file)
        with open(json_file) as f:
            json_data = json.load(f)
        inputData = Input(json_data,None,None,None)
    else:
        logger.info("Processing message with id: "+json_message["MessageId"])
        messageId = json_message["MessageId"]
        logger.info(json_message['Body'])
        inputData = Input(json.loads(json_message['Body']), logger, queue, json_message["ReceiptHandle"])

    start_date = inputData.start_date()
    start_date_pmb = inputData.start_date_pmb()
    end_date = inputData.end_date()
    end_date_pmb = inputData.end_date_pmb()
    time_step = inputData.time_step()

    s3 = S3file(os.environ["OUTPUT_BUCKET"])

    db = Database()
    owi_field = pymetbuild.OwiAscii(start_date_pmb,end_date_pmb,time_step)

    nowcast = inputData.nowcast()
    multiple_forecasts = inputData.multiple_forecasts()

    domain_data = []
    for i in range(inputData.num_domains()):
        d = inputData.domain(i)
        fn1 = inputData.filename()+"_"+"{:02d}".format(i)+".pre"
        fn2 = inputData.filename()+"_"+"{:02d}".format(i)+".wnd"
        owi_field.addDomain(d.grid().grid_object(),fn1,fn2)
        f = db.generate_file_list(d.service(),start_date,end_date,d.storm(),nowcast,multiple_forecasts) 
        if len(f) < 2:
            logger.error("No data found for domain "+str(i)+". Giving up.")
            if not json_file:
                logger.debug("Deleting message "+message["MessageId"]+" from the queue")
                queue.delete_message(message["ReceiptHandle"])
            sys.exit(1)

        domain_data.append([])
        for item in f:
            local_file = db.get_file(item[1],d.service(),item[0])
            domain_data[i].append({"time":item[0],"filepath":local_file})
        

    output_file_list=[]
    for i in range(inputData.num_domains()):
        d = inputData.domain(i)
        met = pymetbuild.Meteorology(d.grid().grid_object())
        fn1 = inputData.filename()+"_"+"{:02d}".format(i)+".pre"
        fn2 = inputData.filename()+"_"+"{:02d}".format(i)+".wnd"
        output_file_list.append(fn1)
        output_file_list.append(fn2)
        t0 = domain_data[i][0]["time"]
        t1 = domain_data[i][1]["time"]
        t0_pmb = Input.date_to_pmb(t0)
        t1_pmb = Input.date_to_pmb(t1)
        index = 1
        met.set_next_file(domain_data[i][0]["filepath"])
        met.set_next_file(domain_data[i][1]["filepath"])
        for t in datespan(start_date,end_date,datetime.timedelta(seconds=time_step)): 
            print(t)
            if t > t1:
                index += 1
                t0 = t1
                t1 = domain_data[i][index]["time"]
                print(t0, t1, t, domain_data[i][index]["filepath"])
                met.set_next_file(domain_data[i][index]["filepath"])
                met.process_data()
            weight = met.generate_time_weight(Input.date_to_pmb(t0),
                    Input.date_to_pmb(t1),Input.date_to_pmb(t))
            values = met.to_wind_grid(weight)
            owi_field.write(Input.date_to_pmb(t),i,values)

        if not json_file:
            path1 = messageId + "/" + fn1
            path2 = messageId + "/" + fn2
            s3.upload_file(fn1,path1)
            s3.upload_file(fn2,path2)

    if json_file:
        logger.info("Finished processing file: "+json_file)
    else:
        output_file_dict = {"files":output_file_list}
        filelist_path = messageId+"/"+filelist_name
        with open(filelist_name,'w') as of:
            of.write(json.dumps(output_file_dict))
        s3.upload_file(filelist_name,filelist_path)
        logger.info("Finished processing message with id: "+json_message["MessageId"])

    cleanup_temp_files(domain_data)

    instance.disable_termination_protection()

    return


def cleanup_temp_files(data):
    import os
    for domain in data:
        for f in domain:
            os.remove(f["filepath"])


def initialize_environment_variables():
    import os
    import boto3
    import requests

    region = requests.get("http://169.254.169.254/latest/meta-data/placement/availability-zone").text[0:-1]
    ec2 = boto3.client("ec2",region_name=region)
    ssm = boto3.client("ssm",region_name=region)
    stackname = ec2.describe_tags(Filters=[{"Name":"key","Values":["aws:cloudformation:stack-name"]}])["Tags"][0]["Value"]
    dbpassword = ssm.get_parameter(Name=stackname+"-dbpassword")["Parameter"]["Value"]
    dbusername = ssm.get_parameter(Name=stackname+"-dbusername")["Parameter"]["Value"]
    dbserver = ssm.get_parameter(Name=stackname+"-dbserver")["Parameter"]["Value"]
    dbname = ssm.get_parameter(Name=stackname+"-dbname")["Parameter"]["Value"]
    bucket = ssm.get_parameter(Name=stackname+"-bucket")["Parameter"]["Value"]
    outbucket = ssm.get_parameter(Name=stackname+"-outputbucket")["Parameter"]["Value"]
    queue = ssm.get_parameter(Name=stackname+"-queue")["Parameter"]["Value"]

    os.environ["DBPASS"] = dbpassword
    os.environ["DBUSER"] = dbusername
    os.environ["DBSERVER"] = dbserver
    os.environ["DBNAME"] = dbname
    os.environ["BUCKET"] = bucket
    os.environ["OUTPUT_BUCKET"] = outbucket
    os.environ["QUEUE_NAME"] = queue
    os.environ["AWS_DEFAULT_REGION"] = region


# Main function
# Check for a message in the queue. If it exists, process it
# otherwise, we're outta here
def main():
    from metbuild.queue import Queue
    import sys
    import os

    logger.debug("Beginning execution")

    initialize_environment_variables()

    if len(sys.argv)==2:
        jsonfile = sys.argv[1]
        if os.path.exists(jsonfile): 
            process_message(None,None,json_file=jsonfile)
        else:
            print("[ERROR]: File "+jsonfile+" does not exist.")
            exit(1)
    else:
        queue = Queue(logger)
        
        has_message,message = queue.get_next_message()
        if has_message:
            logger.debug("Found message in queue. Beginning to process")
            process_message(message, queue)
            logger.debug("Deleting message "+message["MessageId"]+" from the queue")
            queue.delete_message(message["ReceiptHandle"])
        else:
            logger.info("No message available in queue. Shutting down.")

    logger.debug("Exiting script with status 0")
    exit(0)


if __name__ == "__main__":
    main()
