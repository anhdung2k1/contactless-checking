from socket_client import *

def main():
    socket_client = SocketClient()
    socket_client.socket_init()
    socket_client.sendRequest("LOGIN_USER|anhdung1")
    time.sleep(2)
    socket_client.sendRequest("LOGIN_PASSWORD|anhdung1")
    socket_client.receiveResponse()
    
if __name__ == "__main__":
    main()