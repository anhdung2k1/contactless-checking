from socket_client import *

def main():
    socket_client = SocketClient()
    socket_client.socket_init()
    socket_client.sendRequest("REGISTER_USER|anhdung1")
    time.sleep(5)
    socket_client.sendRequest("REGISTER_PASSWORD|anhdung1")
    socket_client.receiveResponse()
    
if __name__ == "__main__":
    main()