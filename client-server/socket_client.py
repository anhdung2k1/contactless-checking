import socket
import os
import time

class SocketClient:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_serviceName = socket.gethostbyname(os.getenv('SERVER_HOST'))
        self.server_port = 8000
        
    def socket_init(self):
        server_address = (self.server_serviceName, self.server_port)
        self.client_socket.connect(server_address)
        print("Connected to the server")

    def sendRequest(self, message):
        self.client_socket.send(message.encode())
    
    def receiveResponse(self):
        return self.client_socket.recv(1024).decode()
        
    def socket_close(self):
        self.client_socket.close()