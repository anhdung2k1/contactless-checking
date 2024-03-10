// Copyright [2024] <Anh Dung>
#include "ServerController.h"
#include "../services/ServerService.h"

#define PORT 8000
struct ServerService::Client {
    int sock;
    User user;
    CURL *curl;
    struct curl_slist *slist;
};

void ServerController::connectToClient() {
    int serverFd, addrlen;
    struct sockaddr_in address;
    int maxClient=10;
    string apiIp = "http://" + string(getenv("API_HOST")) + ":8080/api";
    string mysqlIp = string(getenv("DB_HOST"));
    map<int, ServerService::Client> clientMap;
    bool establishConnection = ServerService::handleConnect(serverFd, maxClient, addrlen, address, false, PORT);
    if (establishConnection) {
        pollfd fds[maxClient];
        ServerService::HandleMultiClient(clientMap, maxClient, serverFd, address, addrlen, fds, apiIp, mysqlIp);
    } else {
        exit(1);
    }
}