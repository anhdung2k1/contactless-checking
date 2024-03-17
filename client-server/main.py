from socket_client import *

def main():
    server_address = "zrdtuan-ns.ck-server.com"
    server_port = 80
    socket_client = SocketClient(server_address=server_address, server_port=server_port)
    socket_client.socket_init()
    socket_client.sendRequest("LOGIN_USER|anhdung1")
    time.sleep(2)
    socket_client.sendRequest("LOGIN_PASSWORD|anhdung1")
    socket_client.receiveResponse()
    
if __name__ == "__main__":
    main()