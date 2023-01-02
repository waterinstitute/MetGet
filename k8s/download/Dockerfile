FROM ubuntu:22.04

RUN apt-get update && apt-get install -y ca-certificates python3 python3-pip openssl

COPY requirements.txt /tmp/

RUN pip install --requirement /tmp/requirements.txt

WORKDIR /app

COPY metgetlib /app/metgetlib/.
COPY metget_download.py /app/. 
