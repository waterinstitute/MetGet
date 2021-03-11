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
def lambda_function(event, context):
    from input import Input

    # Parse the json event data
    input_data = Input(event)

    # Query the data based upon the json input file
    query_database(input_data)

    # Build the wind files
    output_files = create_wind_file(input_data)

    # Upload the data to S3
    uploaded_data = upload_data(input_data, output_files)

    # Return the response
    return {
        "statusCode": 200,
        "body": {
            "message": "Data retrieved from the MetGet system",
            "version": "0.0.1",
            "request": input_data.uuid(),
            "uploaded_files": uploaded_data
        },
    }


def upload_data(input_data, output_files):
    import boto3
    import os
    client = boto3.client('s3')
    upload_bucket = "metgetoutput"
    upload_location = "https://" + upload_bucket + ".s3.amazonaws.com/" + input_data.uuid(
    )

    uploaded_files = []

    for file in output_files:
        fn1 = file.split("/")[-1]
        print("[INFO]: Uploading to S3 bucket (" + upload_bucket + "): " + fn1)
        client.upload_file(file, upload_bucket, input_data.uuid() + "/" + fn1)
        uploaded_files.append(upload_location + "/" + fn1)
        os.remove(file)

    return uploaded_files


def create_wind_file(input_data):
    from datetime import timedelta

    # Initialize the output files
    file_list, output_file = initialize_output(input_data)

    # Iterate on wind file time snaps
    itdate = input_data.start_date()
    while itdate <= input_data.end_date():
        for i in range(input_data.num_domains()):
            uvp = input_data.domain(i).met_data().interpolate_to_grid(
                itdate,
                input_data.domain(i).grid())
            output_file[i].write_record(itdate, uvp)
        itdate += timedelta(seconds=input_data.time_step())

    # Close output files
    for of in output_file:
        of.close()

    return file_list


def initialize_output(input_data):
    from owi import Owi
    import tempfile
    output_files = []
    file_list = []
    for i in range(input_data.num_domains()):
        fn1 = tempfile.gettempdir() + "/" + input_data.filename(
        ) + ".domain_{:02d}.221".format(i)
        fn2 = tempfile.gettempdir() + "/" + input_data.filename(
        ) + ".domain_{:02d}.222".format(i)
        file_list.append(fn1)
        file_list.append(fn2)
        output_files.append(
            Owi(
                input_data.domain(0).grid(), input_data.start_date(),
                input_data.end_date(), fn1, fn2))
        output_files[-1].open()
    return file_list, output_files


def query_database(input_data):
    from database import Database
    from metdata import Metdata
    debug = False

    db = Database()
    for i in range(input_data.num_domains()):
        print("[INFO]: Initializing domain: ", i,
              " with data from: " + input_data.domain(i).service())
        file_list = db.generate_file_list(
            input_data.domain(i).service(), input_data.start_date(),
            input_data.end_date())
        time_list = []
        local_files = []
        for file in file_list:
            local_files.append(
                db.get_file(file[1],
                            input_data.domain(i).service(),
                            file[0],
                            dry_run=debug))
            time_list.append(file[0])
        input_data.domain(i).set_met_data(
            Metdata(input_data.domain(i).service(), local_files, time_list))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    import json

    with open('json_input.json') as f:
        json_input = json.load(f)
    ctx = "context"
    ret = lambda_function(json_input, ctx)

    print(ret)
