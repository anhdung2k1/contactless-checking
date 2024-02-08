import socket
import time

class SocketClient:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = "172.17.0.4"
        self.server_port = 8000
        
    def socket_init(self):
        server_address = (self.server_ip, self.server_port)
        self.client_socket.connect(server_address)
        print("Connected to the server")

    def sendRequest(self,message):
        self.client_socket.send(message.encode())
        
    def socket_close(self):
        self.client_socket.close()