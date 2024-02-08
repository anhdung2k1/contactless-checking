// Copyright [2024] <Anh Dung>
#include "ServerService.h"

using std::cout;
using std::endl;
using std::string;
using std::stringstream;
using std::thread;
using std::to_string;
using std::vector;

string ServerService::ConvertIntToString(int id)
{
    stringstream ss;
    ss << id;
    string s;
    ss >> s;
    return s;
}

void ServerService::CheckConnected(int new_socket, bool flag)
{
    if (!flag)
    {
        close(new_socket);
        return;
    }
}

void ServerService::SendResponse(int new_socket, string response)
{
    if (!send(new_socket, response.c_str(), 1024, 0))
    {
        cout << "Failed!\n";
    }
}

struct ServerService::Client
{
    int sock;
    User user;
    CURL *curl;
    CURLcode res;
    struct curl_slist *slist;
};

bool ServerService::ReadResponse(Client client, char *buffer, map<int, Client> clientMap)
{
    int bytes_received = recv(client.sock, buffer, 1024, 0);
    if (bytes_received <= 0)
    {
        cout << "User " << client.user.getName() << " has disconnected" << endl;
        return false;
    }
    return true;
}

void ServerService::RemoveClient(map<int, Client> &clientMap, Client client, pollfd fds[], int i)
{
    clientMap.erase(client.sock);
    fds[i].fd = -1;
}

void ServerService::processPattern(char *buffer, string &pattern, string &value)
{
    string convertedBuffer = (string)buffer;
    int pos = convertedBuffer.find("|");
    pattern = convertedBuffer.substr(0, pos);
    value = convertedBuffer.substr(pos + 1);
}
bool ServerService::handleClient(map<int, Client> &clientMap, Client &client, pollfd fds[], int i, string apiIp, string mysqlIp)
{
    char buffer[1024];
    CurlUtils curlUtils;
    stringstream formData;
    string pattern, value;
    bool flag = true;
    bzero(buffer, 1024);
    // Receive data from client
    if (!ReadResponse(client, buffer, clientMap))
    {
        close(client.sock);
        RemoveClient(clientMap, client, fds, i);
        return false;
    }
    cout << buffer << endl;
    processPattern(buffer, pattern, value);

    if (pattern == "LOGIN_USER")
    {
        flag = Repository::CheckUserName(value, mysqlIp);
        if (flag)
        {
            client.user.setName(value);
        }
        SendResponse(client.sock, "LOGIN_USER|" + to_string(flag));
    }
    else if (pattern == "LOGIN_PASSWORD")
    {
        client.user.setPassword(value);
        // Call API
        formData << "{\"userName\": "
                 << "\"" + client.user.getName() << "\","
                 << "\"password\": "
                 << "\"" << client.user.getPassword() << "\"}";
        // cout << formData.str() << endl;
        curlUtils.authUtil(apiIp + "/accounts/signin", formData.str(), flag, client.curl, client.res, client.slist);
        if (flag)
        {
            string response = curlUtils.getUtil(client.curl, client.res, apiIp + "/users/find?user_name=" + client.user.getName(), flag);
            nlohmann::json j = nlohmann::json::parse(response);
            client.user.setId(j.at("user_id"));
        }
        SendResponse(client.sock, "LOGIN_PASSWORD|" + to_string(flag));
    }
    else if (pattern == "REGISTER_USER")
    {
        flag = !Repository::CheckUserName(value, mysqlIp);
        if (flag)
        {
            client.user.setName(value);
        }
        SendResponse(client.sock, "REGISTER_USER|" + to_string(flag));
    }
    else if (pattern == "REGISTER_PASSWORD")
    {
        client.user.setPassword(value);
        // Call API
        formData << "{\"userName\": "
                 << "\"" + client.user.getName() << "\","
                 << "\"password\": "
                 << "\"" << client.user.getPassword() << "\"}";
        curlUtils.authUtil(apiIp + "/accounts/signup", formData.str(), flag, client.curl, client.res, client.slist);
        if (flag)
        {
            string response = curlUtils.getUtil(client.curl, client.res, apiIp + "/users/find?user_name=" + client.user.getName(), flag);
            nlohmann::json j = nlohmann::json::parse(response);
            client.user.setId(j.at("user_id"));
        }
        SendResponse(client.sock, "REGISTER_PASSWORD|" + to_string(flag));
    }
    else if (pattern == "LOGOUT_USER")
    {
        curlUtils.handleDestruct(client.curl, client.slist);
        // cout << "User "<< client.user.getName() << " has logged out!\n";
        client.user.setId(-1);
        client.user.setName("");
        client.user.setPassword("");
        flag = true;
    }
    else if (pattern == "FIND_USER")
    {
        string response = curlUtils.getUtil(client.curl, client.res, apiIp + "/users/search?userName=" + value, flag);
        SendResponse(client.sock, "FIND_USER|" + response);
    }
    else if (pattern == "UPDATE_PROFILE")
    {
        string response = curlUtils.getUtil(client.curl, client.res, apiIp + "/users/" + ConvertIntToString(client.user.getId()), flag);
        // cout << ConvertIntToString(client.user.getId()) << endl;
        // cout << response << endl;
        nlohmann::json j = nlohmann::json::parse(response);
        if (j.at("address").is_null())
        {
            j.at("address") = to_string(j.at("address"));
        }
        if (j.at("gender").is_null())
        {
            j.at("gender") = to_string(j.at("gender"));
        }
        client.user.setAddress(j.at("address"));
        client.user.setGender(j.at("gender"));
        SendResponse(client.sock, "UPDATE_PROFILE|" + response);
    }
    else if (pattern == "UPDATE_ADDRESS")
    {
        formData << "{\"address\": \"" + value + "\",\"gender\": \"" + client.user.getGender() + "\"}";
        // cout << formData.str() << endl;
        string response = curlUtils.patchUtil(client.curl, client.res, apiIp + "/users/" + ConvertIntToString(client.user.getId()), formData.str(), flag);
    }
    else if (pattern == "UPDATE_GENDER")
    {
        formData << "{\"address\": \"" + client.user.getAddress() + "\",\"gender\": \"" + value + "\"}";
        // cout << formData.str() << endl;
        string response = curlUtils.patchUtil(client.curl, client.res, apiIp + "/users/" + ConvertIntToString(client.user.getId()), formData.str(), flag);
    }
    else if (pattern == "CHANGE_PASSWORD")
    {
        formData << "{\"password\": \"" + value + "\"}";
        // cout << formData.str() << endl;
        // cout << client.user.getName() << " changed password!\n";
        string accountId = curlUtils.getUtil(client.curl, client.res, apiIp + "/accounts/find?userName=" + client.user.getName(), flag);
        string url = apiIp + "/accounts/" + accountId;
        string response = curlUtils.putUtil(client.curl, client.res, url, formData.str(), flag);
    }
    else if (pattern == "USER_EXIT_APP")
    {
        close(client.sock);
        RemoveClient(clientMap, client, fds, i);
        flag = true;
        SendResponse(client.sock, "USER_EXIT_APP|True");
    }
    else if (pattern == "USER_PROFILE")
    {
        string response = curlUtils.getUtil(client.curl, client.res, apiIp + "/users/" + value, flag);
        cout << response << endl;
        nlohmann::json j = nlohmann::json::parse(response);
        if (j.at("userName").is_null())
        {
            j.at("userName") = to_string(j.at("userName"));
        }
        if (j.at("address").is_null())
        {
            j.at("address") = to_string(j.at("address"));
        }
        if (j.at("gender").is_null())
        {
            j.at("gender") = to_string(j.at("gender"));
        }
        client.user.setName(j.at("userName"));
        client.user.setAddress(j.at("address"));
        client.user.setGender(j.at("gender"));
        SendResponse(client.sock, "USER_PROFILE|" + response);
    }
    else if (pattern == "ACTIVATE_THREAD")
    {
        SendResponse(client.sock, "|");
    }
    else if (pattern == "RECONNECT")
    {
        nlohmann::json j = nlohmann::json::parse(value);
        client.user.setName(j.at("userName"));
        client.user.setPassword(j.at("userPassword"));
        formData << "{\"userName\": "
                 << "\"" + client.user.getName() << "\","
                 << "\"password\": "
                 << "\"" << client.user.getPassword() << "\"}";
        curlUtils.authUtil(apiIp + "/accounts/signin", formData.str(), flag, client.curl, client.res, client.slist);
        if (flag)
        {
            string response = curlUtils.getUtil(client.curl, client.res, apiIp + "/users/find?user_name=" + client.user.getName(), flag);
            nlohmann::json j = nlohmann::json::parse(response);
            client.user.setId(j.at("user_id"));
        }
        SendResponse(client.sock, "RECONNECT|");
    }
    return flag;
}

bool ServerService::handleConnect(int &serverFd, int maxClient, int &addrlen, struct sockaddr_in &address, bool isLocal, int port)
{
    int opt = 1;
    addrlen = sizeof(address);
    // Creating socket file descriptor
    if ((serverFd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        perror("socket failed");
        return false;
    }
    // Forcefully attaching socket to the port 8080
    if (setsockopt(serverFd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt)))
    {
        perror("setsockopt");
        return false;
    }
    address.sin_family = AF_INET;
    if (isLocal)
    {
        address.sin_addr.s_addr = inet_addr("127.0.0.1");
    }
    else
    {
        address.sin_addr.s_addr = INADDR_ANY;
    }
    address.sin_port = htons(port);
    // Forcefully attaching socket to the port 8080
    if (bind(serverFd, (struct sockaddr *)&address, sizeof(address)) < 0)
    {
        perror("bind failed");
        return false;
    }
    return true;
}

void ServerService::ProcessPollValue(map<int, Client> &clientMap, int maxClient, pollfd fds[], int serverFd, int &addrlen, struct sockaddr_in &address, int timeout, string apiIp, string mysqlIp)
{
    int nready = poll(fds, maxClient, timeout);
    if (nready < 0)
    {
        perror("failed to poll file descriptors");
        exit(EXIT_FAILURE);
    }
    for (int i = 0; i < maxClient; i++)
    {
        if (fds[i].revents & POLLIN)
        {
            if (i == 0)
            {
                // Accept new connection
                int clientSocket = accept(serverFd, (struct sockaddr *)&address, (socklen_t *)&addrlen);
                if (clientSocket < 0)
                {
                    perror("Failed to accept connection");
                    exit(EXIT_FAILURE);
                }
                Client client;
                client.sock = clientSocket;
                for (int j = 1; j < 10; j++)
                {
                    if (fds[j].fd == -1)
                    {
                        fds[j].fd = clientSocket;
                        clientMap[clientSocket] = client;
                        break;
                    }
                    if (j >= maxClient)
                    {
                        cout << "Coredump" << endl;
                    }
                }
            }
            else
            {
                handleClient(clientMap, clientMap[fds[i].fd], fds, i, apiIp, mysqlIp);
            }
        }

        else if (fds[i].revents & POLLHUP)
        {
            cout << fds[i].fd << " closed!\n";
        }
    }
}

void ServerService::ListenToClient(pollfd fds[], int serverFd, int maxClient)
{
    if (listen(serverFd, maxClient) < 0)
    {
        perror("listen");
        exit(1);
    }

    for (int i = 0; i < maxClient; i++)
    {
        fds[i].fd = -1;
        fds[i].events = POLLIN;
    }

    fds[0].fd = serverFd;
    fds[0].events = POLLIN;
}

void ServerService::HandleMultiClient(map<int, Client> &clientMap, int maxClient, int serverFd,
                                          struct sockaddr_in &address, int &addrlen, pollfd fds[], string apiIp, string mysqlIp)
{
    ListenToClient(fds, serverFd, maxClient);
    while (1)
    {
        ProcessPollValue(clientMap, maxClient, fds, serverFd, addrlen, address, -1, apiIp, mysqlIp);
    }
}

void ServerService::ShutDownServer(int serverFd)
{
    // closing the listening socket
    shutdown(serverFd, SHUT_RDWR);
}