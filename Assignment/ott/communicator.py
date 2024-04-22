from socket import *
import threading


class Communicator:
    def __init__(self, ip, port, msg_handler):
        self.ip = ip
        self.port = int(port)
        self.msg_handler = msg_handler
        print(f"Communicator Started at {ip}:{port}")
        listener = threading.Thread(target=self.listen_msg)
        listener.start()
        return

    def send_msg(self, message):
        clientSocket = socket(AF_INET, SOCK_DGRAM)
        clientSocket.sendto(message.encode(), (self.ip, self.port))
        clientSocket.close()

    def listen_msg(self):
        print(f"Communicator listing at {self.ip}:{self.port}")
        serverSocket = socket(AF_INET, SOCK_DGRAM)
        serverSocket.bind(("", self.port))
        while True:
            message, clientAddress = serverSocket.recvfrom(2048)
            self.msg_handler(([message, clientAddress]))
            break


# Uncomment following lines for testing.
# def handler(message, clientAddress):
#     print("Message from ", clientAddress, ": ", message)

# message = input("Type message to send")
# comm1 = Communicator(ip="localhost", port=12000, msg_handler=handler)
# comm1.send_msg(message=message)
