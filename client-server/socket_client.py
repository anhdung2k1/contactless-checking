import socket
import os
import time

class SocketClient:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = "172.17.0.5"
        self.server_port = 8000
        
    def socket_init(self):
        server_address = (self.server_ip, self.server_port)
        self.client_socket.connect(server_address)
        print("Connected to the server")

    def sendRequest(self, message):
        try:
            self.client_socket.sendall(message.encode())
        except Exception as e:
            print(f"Error occurred while sending the request: {e}")
    
    def receiveResponse(self):
        try:
            return self.client_socket.recv(1024).decode()
        except Exception as e:
            print(f"Error occurred while receiving the response: {e}")
            return None
        
    def socket_close(self):
        try:
            self.client_socket.close()
            print("Socket closed")
        except Exception as e:
            print(f"Error occurred while closing the socket: {e}")