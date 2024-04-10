import socket
import threading

class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        

    def start(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

        nickname = input("Enter your nickname: ")
        self.client_socket.send(nickname.encode())

        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

        self.display_menu()

    def display_menu(self):
        menu = "\nChoose your options\n"
        menu += "1. Send a broadcast message\n"
        menu += "2. Send a private message\n"
        menu += "3. Create a channel\n"
        menu += "4. Join a channel\n"
        menu += "5. Send message in channel\n"
        menu += "6. Quit\n"
        print(menu)
        self.handle_choice()

    def join_channel(self, channel_name):
        self.client_socket.send(f"/join {channel_name}".encode())

    def send_message_to_channel(self, message, channel_name):
        self.client_socket.send(f"{channel_name}: {message}".encode())

    def handle_choice(self):
        while True:
            choice = input("Enter your choice: ")
            if choice == "1":
                message = input("Enter your message: ")
                self.client_socket.send(message.encode())
            elif choice == "3":
                channel_name = input("Enter channel name: ")
                self.client_socket.send(f"/create_channel {channel_name}".encode())
            elif choice == "4":
                channel_name = input("Enter channel name to join: ")
                self.client_socket.send(f"/join {channel_name}".encode())
            elif choice == "2":
                receiver = input("Enter receiver's nickname: ")
                message = input("Enter your message: ")
                self.client_socket.send(f"/private {receiver} {message}".encode())
            elif choice == "5":
                channel_name = input("Enter channel name: ")
                message = input("Enter your message: ")
                self.client_socket.send(f"{channel_name}:{message}".encode())
            elif choice == "6":
                self.client_socket.send("/quit".encode())
                self.client_socket.close()
                break
            else:
                print("Invalid choice. Please choose again.")
            self.display_menu()

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                print(message)
            except Exception as e:
                print(e)
                break

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 3000
    client = ChatClient(HOST, PORT)
    client.start()
