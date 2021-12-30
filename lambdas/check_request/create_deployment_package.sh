#!/bin/bash

rm -rf package
rm -rf metget-checkstatus.zip

mkdir package
pip install --target ./package pymysql

cd package
zip -gr ../metget-checkstatus.zip *
cd .. 
zip -g metget-checkstatus.zip lambda_function.py 
