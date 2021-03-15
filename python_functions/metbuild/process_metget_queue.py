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
def process_message(json_message):
    import time
    import json
    import pymetbuild
    import datetime
    import os
    from metbuild.instance import Instance
    from metbuild.input import Input
    from metbuild.database import Database
    from metbuild.s3file import S3file

    instance = Instance()

    instance.enable_termination_protection()

    logger.info("Processing message with id: "+json_message["MessageId"])
    messageId = json_message["MessageId"]

    logger.info(json_message['Body'])

    inputData = Input(json.loads(json_message['Body']))
    start_date = inputData.start_date()
    start_date_pmb = inputData.start_date_pmb()
    end_date = inputData.end_date()
    end_date_pmb = inputData.end_date_pmb()
    time_step = inputData.time_step()

    s3 = S3file(os.environ["OUTPUT_BUCKET"])

    db = Database()
    owi_field = pymetbuild.OwiAscii(start_date_pmb,end_date_pmb,time_step)

    domain_data = []
    for i in range(inputData.num_domains()):
        d = inputData.domain(i)
        fn1 = inputData.filename()+"_"+"{:02d}".format(i)+".pre"
        fn2 = inputData.filename()+"_"+"{:02d}".format(i)+".wnd"
        owi_field.addDomain(d.grid().grid_object(),fn1,fn2)
        f = db.generate_file_list(d.service(),start_date,end_date) 

        domain_data.append([])
        for item in f:
            local_file = db.get_file(item[1],d.service(),item[0])
            domain_data[i].append({"time":item[0],"filepath":local_file})
        

    for i in range(inputData.num_domains()):
        d = inputData.domain(i)
        met = pymetbuild.Meteorology(d.grid().grid_object())
        fn1 = inputData.filename()+"_"+"{:02d}".format(i)+".pre"
        fn2 = inputData.filename()+"_"+"{:02d}".format(i)+".wnd"
        t0 = domain_data[i][0]["time"]
        t1 = domain_data[i][1]["time"]
        t0_pmb = Input.date_to_pmb(t0)
        t1_pmb = Input.date_to_pmb(t1)
        index = 1
        met.set_next_file(domain_data[i][0]["filepath"])
        met.set_next_file(domain_data[i][1]["filepath"])
        met.process_data()
        for t in datespan(start_date,end_date,datetime.timedelta(seconds=time_step)): 
            if t > t1:
                index += 1
                t0 = t1
                t1 = domain_data[i][index]["time"]
                met.set_next_file(domain_data[i][index]["filepath"])
            weight = met.generate_time_weight(Input.date_to_pmb(t0),
                    Input.date_to_pmb(t1),Input.date_to_pmb(t))
            values = met.to_wind_grid(weight)
            owi_field.write(Input.date_to_pmb(t),i,values)

        path1 = messageId + "/" + fn1
        path2 = messageId + "/" + fn2
        s3.upload_file(fn1,path1)
        s3.upload_file(fn2,path2)



    logger.info("Finished processing message with id: "+json_message["MessageId"])

    instance.disable_termination_protection()

    return


# Main function
# Check for a message in the queue. If it exists, process it
# otherwise, we're outta here
def main():
    from metbuild.queue import Queue
    logger.debug("Beginning execution")

    queue = Queue(logger)
    
    has_message,message = queue.get_next_message()
    if has_message:
        logger.debug("Found message in queue. Beginning to process")
        process_message(message)
        logger.debug("Deleting message "+message["MessageId"]+" from the queue")
        queue.delete_message(message["ReceiptHandle"])
    else:
        logger.info("No message available in queue. Shutting down.")

    logger.debug("Exiting script with status 0")
    exit(0)


if __name__ == "__main__":
    main()
