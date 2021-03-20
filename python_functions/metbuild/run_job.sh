#!/bin/bash

#...Name of script to retrieve and run
script=process_metget_queue.py

#...Time between consecutive runs
sleepytime=10

#...Get the script from s3
echo "Getting the main script from S3"
aws s3 cp s3://metget-scripts/metbuild . --recursive
chmod ug+x /home/ec2-user/$script

#...Get the environment variables
stack=metget-stack01
region=us-east-1
export DBPASS=$(aws --region=$region ssm get-parameter --name "$stack-dbpassword" --query Parameter.Value --output text)
export DBUSER=$(aws --region=$region ssm get-parameter --name "$stack-dbusername" --query Parameter.Value --output text)
export DBSERVER=$(aws --region=$region ssm get-parameter --name "$stack-dbserver" --query Parameter.Value --output text)
export DBNAME=$(aws --region=$region ssm get-parameter --name "$stack-dbname" --query Parameter.Value --output text)
export BUCKET=$(aws --region=$region ssm get-parameter --name "$stack-bucket" --query Parameter.Value --output text)
export OUTPUT_BUCKET=$(aws --region=$region ssm get-parameter --name "$stack-outputbucket" --query Parameter.Value --output text)
export QUEUE_NAME=$(aws --region=$region ssm get-parameter --name "$stack-queue" --query Parameter.Value --output text)

#...Infinite loop to process queue messages
while [[ 0 == 0 ]] 
do
    echo "Processing data at $(date)"
    stat=$(python3 /home/ec2-user/$script)
    echo $stat
    python3 /home/ec2-user/$script
    echo "Sleeping for $sleepytime seconds"
    sleep $sleepytime 
done

