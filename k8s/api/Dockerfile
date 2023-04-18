FROM ubuntu:22.04

RUN apt-get update && apt-get install -y ca-certificates python3 python3-pip openssl libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/

RUN pip install --requirement /tmp/requirements.txt

WORKDIR /app

COPY metget.py /app/. 
COPY metget_api /app/metget_api/.

ENTRYPOINT ["gunicorn"]
CMD ["-w","4","metget:application","--bind","0.0.0.0:8080"]
