import threading
import time, socket, logging
from threading import Thread
from queue import Queue
from data_structures import MutexMessage, MutexNode

MSG_TYPE_REQUEST = 1
MSG_TYPE_REPLY = 2

Max_Msg_length = 4096
delay_quantum = 5
ip = socket.gethostbyname(socket.gethostname())
port_number = 6100
ip_address = f"{ip}:{port_number}"


class MediaProvider(Thread):
    def __init__(self, node, other_nodes, task):
        super().__init__(None, target=task)
        print("Constructor")
        listener = threading.Thread(target=self.msg_listener)
        self.request_pending = Queue()
        self.msg_queue = Queue()
        self.delay = 5
        self.node = node
        self.other_nodes = other_nodes
        listener.start()

    def msg_listener(self):
        print(f"Mutex provider started at {ip_address} ###############.")
        listeningSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Bind the socket to the local address
        listeningSocket.bind(("", self.node.port))
        while True:
            self.handle_message(listeningSocket.recv(Max_Msg_length))

    def handle_message(self, msg):
        if msg.msg_type == MSG_TYPE_REQUEST:  # request messages
            print(f"<= Request Message Recieved from {msg.node.name}")
            outcome = False
            # condition to check for current process status.
            if outcome:
                self.msg_queue.put(msg)
            else:
                self.send_msg(msg)

        if msg.msg_type == MSG_TYPE_REPLY:  # reply messages
            print(f"<= Reply Message Recieved from {msg.node.name}")
            # remove from the pending set.
            self.request_pending.remove()
        return

    def run(self):
        # send message to all.
        self.request_cs()

        # ensure all the response msgs are recieved or wait.
        self.ensure_all_response()

        # excute the task.
        super().run()

        # handle queued messages.
        self.handle_queued_message()
        return

    def send_msg(self, node, message):
        sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sendSocket.sendto(str(message), node.address)
        sendSocket.close()
        return

    def request_cs(self):
        for node in self.nodes:
            msg = MutexMessage(1, self.node, f"request from {self.name}")
            self.send_msg(node=node, message=msg)
            self.request_pending.add(node)

    def ensure_all_response(self):
        while True:
            if self.request_pending:
                time.sleep(delay_quantum)
            else:
                self.task()

    def handle_queued_message(self):
        # msg = self.msg_queue.get()
        # while msg != None :
        #     msg = self.msg_queue.
        #     self.send_msg()
        return


def printThreadName(name):
    print(name)


# node
current_node = MutexNode(ip="localhost", port=6000, name="P1")

# other_nodes
other_node1 = MutexNode(ip="localhost", port=6001, name="P2")
other_node2 = MutexNode(ip="localhost", port=6002, name="P3")
other_nodes = [other_node1, other_node2]

thread1 = MediaProvider(
    node=current_node, other_nodes=other_nodes, task=printThreadName("mythread")
)
thread1.start()
