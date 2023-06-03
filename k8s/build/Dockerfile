FROM ubuntu:22.04

RUN apt-get update && apt-get install -y ca-certificates python3 python3-pip \
    openssl build-essential swig cmake libnetcdf-dev git libproj-dev libgmp-dev \
    libboost-all-dev libpq-dev libeccodes-dev && rm -rf /var/lib/apt/lists/*

COPY k8s/build/requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt

WORKDIR /app
RUN git clone https://github.com/waterinstitute/metget
RUN mkdir /app/metget/libraries/libmetbuild/build
WORKDIR /app/metget/libraries/libmetbuild/build
RUN cmake .. -DCMAKE_C_COMPILER=gcc \
             -DCMAKE_CXX_COMPILER=g++ \
             -DCMAKE_BUILD_TYPE=Release \
             -DCMAKE_CXX_FLAGS_RELEASE="-O3 -DNDEBUG -march=core-avx2 -mtune=core-avx2" \
             -DCMAKE_C_FLAGS_RELEASE="-O3 -DNDEBUG -march=core-avx2 -mtune=core-avx2"; \
             make -j2 ; make install; cd .. ; rm -rf build

WORKDIR /app

COPY libraries/metbuild /tmp/metbuild/.
RUN pip install /tmp/metbuild/. && rm -rf /tmp/metbuild

COPY k8s/build/*.py /app/. 
