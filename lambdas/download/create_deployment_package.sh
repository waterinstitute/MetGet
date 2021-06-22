#!/bin/bash

rm -rf package
rm -rf metget_deployment.zip

mkdir package
pip install --target ./package pymysql requests bs4 feedparser boto3

cd package
zip -gr ../metget_deployment.zip *
cd .. 
zip -g metget_deployment.zip metgetlib/*
zip -g metget_deployment.zip lambda_function.py 
