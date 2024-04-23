import json
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


class MutexManager(Thread):
    def __init__(self, communicator, node, other_nodes, task, file_name):
        super().__init__(None, target=task, args=([file_name]))
        print("Constructor")
        self.communicator = communicator
        self.request_pending = dict()
        self.msg_queue = Queue()
        self.delay = delay_quantum
        self.node = node
        self.other_nodes = other_nodes
        self.file_name = file_name

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
            key = msg.node.name
            if key in self.request_pending:
                del self.request_pending[key]
                return
            print(f"The key '{key}' does not exist in the dictionary.")
        return

    def run(self):
        # send message to all.
        self.request_cs()

        # ensure all the response msgs are recieved or wait.
        self.ensure_all_response()

        # excute the task.
        super().run()

        # handle queued messages.
        # self.handle_queued_message()
        return

    def send_msg(self, node, message):
        print(node, message)
        self.communicator.send_msg(node, message)
        return

    def request_cs(self):
        msg = MutexMessage(
            1, self.node, f"request from {self.node.name}", file_name=self.file_name
        )
        for node in self.other_nodes:
            print(f"request from {self.node.name}")
            self.send_msg(node=node, message=msg)
            self.request_pending[node.name] = node

    def ensure_all_response(self):
        while True:
            print(f"request_pending for {self.request_pending.keys()}")
            if self.request_pending:
                time.sleep(delay_quantum)
            else:
                break

    def handle_queued_message(self):
        # msg = self.msg_queue.get()
        # while msg != None :
        #     msg = self.msg_queue.
        #     self.send_msg()
        return


def printThreadName(name):
    print(name)


# # node
# current_node = MutexNode(ip="localhost", port=6000, name="P1")

# # other_nodes
# other_node1 = MutexNode(ip="localhost", port=6001, name="P2")
# other_node2 = MutexNode(ip="localhost", port=6002, name="P3")

# thread1 = MediaProvider(
#     node=current_node,
#     other_nodes=[other_node1, other_node2],
#     task=printThreadName,
#     input=["mythread1"],
# )

# # thread1 = threading.Thread(target=printThreadName, args=(["hello world"]))

# thread2 = MediaProvider(
#     node=other_node1,
#     other_nodes=[current_node, other_node2],
#     task=printThreadName,
#     input=["mythread2"],
# )


# thread3 = MediaProvider(
#     node=other_node1,
#     other_nodes=[current_node, other_node2],
#     task=printThreadName("mythread3"),
# )
# thread1.start()
# thread2.start()
# thread3.start()

# thread1.join()
# thread2.join()
