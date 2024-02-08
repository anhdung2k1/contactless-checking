ARG VERSION=22.04
FROM ubuntu:$VERSION

RUN apt-get update && \
    apt-get install build-essential -y
RUN apt-get install g++ -y && \ 
    apt-get install libmysqlclient-dev -y && \
    apt-get install nlohmann-json3-dev -y

RUN apt-get install libcurl4-gnutls-dev -y &&\
    apt-get install libcurl4-openssl-dev -y && \
    apt-get install libcurl4-nss-dev -y

RUN apt-get install libboost-all-dev -y

ARG COMMIT
ARG APP_VERSION
ARG BUILD_TIME

LABEL \
    ck.app.commit=$COMMIT \
    ck.app.version=$APP_VERSION \
    ck.image.title="CK Socket Server" \
    ck.image.created="$BUILD_TIME"

WORKDIR /app/socket-server

COPY socket-server/ /app/socket-server
RUN g++ main.cpp -o server controller/ServerController.cpp services/ServerService.cpp model/User.cpp repository/Repository.cpp utils/CurlUtils.cpp -lcurl -lmysqlclient -lpthread

CMD ["./server"]
