#!/bin/bash

rm -rf package
rm -rf metget-receiverequest.zip

mkdir package
pip install --target ./package pymysql

cd package
zip -r ../metget-receiverequest.zip *
cd .. 
zip -g metget-receiverequest.zip metbuild/*
zip -g metget-receiverequest.zip lambda_function.py 
