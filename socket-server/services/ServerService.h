#pragma once

#include <string.h>
#include <thread>
#include <vector>
#include <iostream>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <sstream>
#include"../model/User.h"
#include"../repository/Repository.h"
#include"../utils/CurlUtils.h"
#include <poll.h>
#include <map>
#include <nlohmann/json.hpp>
#include <boost/range/adaptor/reversed.hpp>

using std::thread;
using std::map;

class ServerService {
    public:
        struct Client;
        static void CheckConnected(int new_socket, bool F);
        static string ConvertIntToString(int id);
        static void SendResponse(int new_socket, string response);
        static bool ReadResponse(Client client, char* buffer, map<int, Client> clientMap);
        static void RemoveClient(map<int, Client>& clientMap, Client client, pollfd fds[], int i);
        static void processPattern(char* buffer, string& pattern, string& value);
        static bool handleClient(map<int, Client>& clientMap, Client& client, pollfd fds[], int i, string apiIp, string mysqlIp);
        static void HandleMultiClient(map<int, Client>& clientMap, int maxClient, int serverFd, struct sockaddr_in& address, int& addrlen, pollfd fds[], string apiIp, string mysqlIp);
        static bool handleConnect(int& serverFd, int maxClient, int& addrlen, struct sockaddr_in& address, bool isLocal, int port);
        static void ProcessPollValue(map<int, Client>& clientMap, int maxClient, pollfd fds[], int serverFd, int& addrlen, struct sockaddr_in& address, int timeout, string apiIp, string mysqlIp);
        static void ListenToClient(pollfd fds[], int serverFd, int maxClient);
        static void ShutDownServer(int serverFd);
};