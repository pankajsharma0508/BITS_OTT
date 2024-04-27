from queue import Queue
import time, socket
from threading import Thread
from data_structures import MutexMessage

MSG_TYPE_REQUEST = 1
MSG_TYPE_REPLY = 2
MUTEX_OPEN = 0
MUTEX_REQUESTED = 1
MUTEX_HELD = 2
Max_Msg_length = 4096
delay_quantum = 5


class MutexManager(Thread):
    def __init__(self, communicator, node, other_nodes, task, file_name, file_hash):
        super().__init__(None, target=task, args=([file_name]))
        self.communicator = communicator
        self.request_pending = dict()
        self.msg_queue = Queue()
        self.delay = delay_quantum
        self.node = node
        self.time_stamp = 1
        self.other_nodes = other_nodes
        self.file_hash = file_hash
        self.file_name = file_name
        self.mutex_status = MUTEX_OPEN

    def handle_message(self, msg):
        if msg.msg_type == MSG_TYPE_REQUEST:  # request messages
            print(f"<= Request Message Recieved from {msg.node.name}")
            can_queue_message = self.check_msg_queue_condition(msg=msg)
            if can_queue_message:
                self.msg_queue.put(msg)
            else:
                reply = MutexMessage(
                    type=MSG_TYPE_REPLY,
                    node=self.node,
                    file_name=msg.file_name,
                    file_hash=msg.file_hash,
                    timestamp=self.time_stamp,
                )
                self.send_msg(msg.node, reply)

        if msg.msg_type == MSG_TYPE_REPLY:  # reply messages
            print(f"Reply Recieved from {msg.node.name}. Updating pending requests")
            # remove from the pending set.
            key = msg.node.name
            if key in self.request_pending:
                del self.request_pending[key]
                print(f"request_pending for {self.request_pending.keys()}")
                return
            print(f"The key '{key}' does not exist in the dictionary.")
        return

    def check_msg_queue_condition(self, msg):
        if (
            int(msg.timestamp) < int(self.time_stamp)
            and self.mutex_status == MUTEX_REQUESTED
        ):
            return True
        if self.mutex_status == MUTEX_HELD:
            return True
        return False

    def run(self):
        print(f"### DME Algorithm Started {self.file_name}.####")
        # send message to all.
        self.request_cs()

        # ensure all the response msgs are recieved or wait.
        self.ensure_all_response()

        # excute the task.
        print(f"Aquiring Mutex and Executing the task {self.file_name}")
        super().run()

        self.handle_queued_message()

        print(f"### DME Algorithm Completed {self.file_name}.####")
        return

    def send_msg(self, node, message):
        self.communicator.send_msg(node, message)
        return

    def request_cs(self):
        msg = MutexMessage(
            type=MSG_TYPE_REQUEST,
            node=self.node,
            file_name=self.file_name,
            file_hash=self.file_hash,
            timestamp=self.time_stamp,
        )
        for node in self.other_nodes:
            print(
                f"### Requesting Critical Section({self.file_hash}) From {node.name}.####"
            )
            self.send_msg(node=node, message=msg)
            self.request_pending[node.name] = node

    def ensure_all_response(self):
        while True:
            if self.request_pending:
                print(f"request_pending for {self.request_pending.keys()}")
                time.sleep(delay_quantum)
            else:
                print(f"****No pending requests***")
                break

    def handle_queued_message(self):
        print(f"Handling queued message if Available")
        while not self.msg_queue.empty():
            request_msg = self.msg_queue.get()
            reply = MutexMessage(
                type=MSG_TYPE_REPLY,
                node=self.node,
                file_name=request_msg.file_name,
                file_hash=request_msg.file_hash,
                timestamp=self.time_stamp,
            )
            self.send_msg(request_msg.node, reply)
        return
