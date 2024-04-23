import json
from socket import *
import threading
from data_structures import MutexMessage, MutexNode


class Communicator:
    def __init__(self, ip, port, msg_handler):
        self.ip = ip
        self.port = int(port)
        self.msg_handler = msg_handler
        print(f"Communicator Started at {ip}:{port}")
        listener = threading.Thread(target=self.listen_msg)
        listener.start()
        return

    def send_msg(self, node, message):
        clientSocket = socket(AF_INET, SOCK_DGRAM)
        clientSocket.sendto(str(message.to_json()).encode(), (self.ip, self.port))
        clientSocket.close()

    def listen_msg(self):
        print(f"Communicator listing at {self.ip}:{self.port}")
        serverSocket = socket(AF_INET, SOCK_DGRAM)
        serverSocket.bind(("", self.port))
        while True:
            message, clientAddress = serverSocket.recvfrom(2048)
            msg = eval(message.decode())
            msg_object = MutexMessage.prepare(msg)
            print(clientAddress)
            self.msg_handler(msg_object, clientAddress)


# Uncomment following lines for testing.
# def handler(message, clientAddress):
#     print("Message from ", clientAddress, ": ", message)


# # message = input("Type message to send")
# node = MutexNode(ip="localhost", port="6000", name="P1")
# message = MutexMessage(type=1, node=node, msg=f"Request")

# comm1 = Communicator(ip="localhost", port=6000, msg_handler=handler)
# comm1.send_msg(message=message)
