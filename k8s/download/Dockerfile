FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y ca-certificates python3 python3-pip openssl postgresql libpq-dev

COPY k8s/download/requirements.txt /tmp/

RUN pip install --requirement /tmp/requirements.txt

COPY libraries/metbuild /tmp/metbuild/.
RUN pip install /tmp/metbuild/. && rm -rf /tmp/metbuild

WORKDIR /app

COPY k8s/download/metgetlib /app/metgetlib/.
COPY k8s/download/metget_download.py /app/. 
