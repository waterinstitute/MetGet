#!/bin/bash

rm -rf package
rm -rf metget-status.zip

mkdir package
pip install --target ./package pymysql

cd package
zip -gr ../metget-status.zip *
cd .. 
zip -g metget-status.zip lambda_function.py 
