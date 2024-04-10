import socket
import threading

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {}
        self.channels = {}

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"New connection from {client_address}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        nickname = client_socket.recv(1024).decode()
        self.clients[nickname] = client_socket

        while True:
            try:
                message = client_socket.recv(1024).decode()
                if message:
                    if ":" in message:  # Check if the message is intended for a channel
                        channel_name, message_content = message.split(":", 1)
                        self.broadcast_message_in_channel(message_content.strip(), nickname, channel_name.strip())
                    elif message.startswith("/create_channel"):
                        self.create_channel(message, client_socket, nickname)
                    elif message.startswith("/join"):
                        self.join_channel(message, nickname)
                    elif message.startswith("/private"):
                        self.send_private_message(message, nickname)
                    else:
                        self.broadcast_message(message, nickname)
                else:
                    raise Exception("Client disconnected")
            except Exception as e:
                print(e)
                del self.clients[nickname]
                client_socket.close()
                break

    def create_channel(self, message, client_socket, nickname):
        channel_name = message.split()[1]
        if channel_name not in self.channels:
            self.channels[channel_name] = [nickname]
            client_socket.send(f"Channel '{channel_name}' created successfully.".encode())
        else:
            client_socket.send(f"Channel '{channel_name}' already exists.".encode())

    def join_channel(self, message, nickname):
        parts = message.split()
        channel_name = parts[1]
        if channel_name not in self.channels:
            self.channels[channel_name] = [nickname]
        else:
            self.channels[channel_name].append(nickname)

    def broadcast_message_in_channel(self, message, sender, channel_name):
        if channel_name in self.channels and sender in self.channels[channel_name]:
            for member in self.channels[channel_name]:
                if member != sender:
                    self.clients[member].send(f"[{sender}@{channel_name}]: {message}".encode())
        else:
            self.clients[sender].send(f"You are not part of '{channel_name}' channel.".encode())

    def send_private_message(self, message, sender):
        parts = message.split()
        receiver = parts[1]
        private_message = ' '.join(parts[2:])
        if receiver in self.clients:
            self.clients[receiver].send(f"[Private from {sender}]: {private_message}".encode())
        else:
            self.clients[sender].send("[Server]: User not found.".encode())

    def broadcast_message(self, message, sender):
        for nickname, client_socket in self.clients.items():
            if nickname != sender:
                client_socket.send(f"[{sender}]: {message}".encode())

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 3000
    server = ChatServer(HOST, PORT)
    server.start()
