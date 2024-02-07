FROM ubuntu:latest

RUN apt-get update && \
    apt install build-essential -y
RUN apt-get install g++ -y && \ 
    apt install libmysqlclient-dev -y && \
    apt-get install nlohmann-json3-dev -y

RUN apt-get install libcurl4-gnutls-dev -y &&\
    apt-get install libcurl4-openssl-dev -y && \
    apt-get install libcurl4-nss-dev -y

RUN apt-get install libboost-all-dev -y


WORKDIR /app

COPY server /app/server
CMD ["./app/server"]
