#!/bin/bash

rm -rf package
rm -rf metget_deployment.zip

mkdir package
pip install --target ./package pymysql requests bs4 feedparser boto3

cd package
zip -gr ../metget-deployment.zip *
cd .. 
zip -g metget-deployment.zip metgetlib/*
zip -g metget-deployment.zip lambda_function.py 
