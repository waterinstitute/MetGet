#!/bin/bash

#...Name of script to retrieve and run
script=process_metget_queue.py

#...Time between consecutive runs
sleepytime=10

#...Get the script from s3
echo "Getting the main script from S3"
aws s3 cp s3://metget-scripts/metbuild . --recursive
chmod ug+x /home/ec2-user/$script

#...Infinite loop to process queue messages
while [[ 0 == 0 ]] 
do
    echo "Processing data at $(date)"
    stat=$(python3 /home/ec2-user/$script)
    echo "Sleeping for $sleepytime seconds"
    sleep $sleepytime 
done

