FROM ubuntu:22.04

RUN apt-get update && apt-get install -y ca-certificates python3 python3-pip openssl libpq-dev && rm -rf /var/lib/apt/lists/*

COPY k8s/api/requirements.txt /tmp/

RUN pip install --requirement /tmp/requirements.txt

WORKDIR /app

COPY libraries/metbuild /tmp/metbuild/.
RUN pip install /tmp/metbuild/. && rm -rf /tmp/metbuild

COPY k8s/api/metget_api /app/metget_api/.
COPY k8s/api/metget.py /app/. 

ENTRYPOINT ["gunicorn"]
CMD ["-w","4","metget:application","--bind","0.0.0.0:8080","--timeout","120"]

#ENTRYPOINT ["python3"]
#CMD [ "metget.py" ]
