#!/bin/bash

rm -rf package
rm -rf metget-statuscache.zip

mkdir package
pip install --target ./package pymysql

cd package
zip -gr ../metget-statuscache.zip *
cd .. 
zip -g metget-statuscache.zip lambda_function.py 
