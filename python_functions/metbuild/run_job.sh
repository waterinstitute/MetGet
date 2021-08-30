#!/bin/bash

region=$(curl http://169.254.169.254/latest/meta-data/placement/availability-zone | sed 's/[a-z]$//')
export AWS_DEFAULT_REGION=us-east-1

instanceid=$(curl http://169.254.169.254/latest/meta-data/instance-id)
awsstack=$(aws ec2 describe-tags --filters "Name=key,Values=aws:cloudformation:stack-name" --output text | head -n 1 | rev | awk -F '\t' '{print $1}' | rev)
if [ "x$awsstack" == "x" ] ; then
    stack="metget-stack01"
else
    stack=$awsstack
fi

logMessage(){
    LogGroupName=$stack-loggroup
    LogStreamName=metbuild_log_$instanceid
    UploadSequenceToken=$(aws logs describe-log-streams --log-group-name "$LogGroupName" --query 'logStreams[?logStreamName==`'$LogStreamName'`].[uploadSequenceToken]' --output text)
    TimeStamp=$(date "+%s%N" --utc)
    TimeStamp=$(expr $TimeStamp / 1000000)
    if [ $UploadSequenceToken == "None" ] ; then
        nextoken=$(aws logs put-log-events --log-group-name "$LogGroupName" --log-stream-name "$LogStreamName" --log-events timestamp=$TimeStamp,message="$1" --output text) 
    else
        nexttoken=$(aws logs put-log-events --log-group-name "$LogGroupName" --log-stream-name "$LogStreamName" --log-events timestamp=$TimeStamp,message="$1" --sequence-token $UploadSequenceToken --output text)
    fi	    
    echo [$(date -R)]: $1
}

logMessage "Running inside stack $stack"
logMessage "Running inside AZ:  $region"

#...Name of script to retrieve and run
script=process_metget_queue.py

#...Time between consecutive runs
sleepytime=10

#...Get the script from s3
logMessage "Getting the main script from S3"
aws s3 cp s3://metget-scripts/metbuild . --recursive
chmod ug+x /home/ec2-user/$script

#...Get the environment variables
export DBPASS=$(aws ssm get-parameter --name "$stack-dbpassword" --query Parameter.Value --output text)
export DBUSER=$(aws ssm get-parameter --name "$stack-dbusername" --query Parameter.Value --output text)
export DBSERVER=$(aws ssm get-parameter --name "$stack-dbserver" --query Parameter.Value --output text)
export DBNAME=$(aws ssm get-parameter --name "$stack-dbname" --query Parameter.Value --output text)
export BUCKET=$(aws ssm get-parameter --name "$stack-bucket" --query Parameter.Value --output text)
export OUTPUT_BUCKET=$(aws ssm get-parameter --name "$stack-outputbucket" --query Parameter.Value --output text)
export QUEUE_NAME=$(aws ssm get-parameter --name "$stack-queue" --query Parameter.Value --output text)

#...Infinite loop to process queue messages
while [[ 0 == 0 ]] 
do
    logMessage "Processing data at $(date)"
    python3 /home/ec2-user/$script
    logMessage "Python returned code $?"
    logMessage "Sleeping for $sleepytime seconds"
    sleep $sleepytime 
done

