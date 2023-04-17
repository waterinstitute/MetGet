FROM ubuntu:22.04

RUN apt-get update && apt-get install -y ca-certificates python3 python3-pip openssl libpq-dev

COPY requirements.txt /tmp/

RUN pip install --requirement /tmp/requirements.txt

WORKDIR /app

COPY *.py /app/. 

CMD ["gunicorn","-w","4","metget:application","--bind","0.0.0.0:8080"]
