import queue
from threading import Thread
import time
from concurrent import futures
import logging
import grpc
import mutex_pb2_grpc
from mutex_pb2 import MessageRequest
import socket

ip = socket.gethostbyname(socket.gethostname())
port_number = 6100
ip_address = f"{ip}:{port_number}" 

class MediaProvider(Thread, mutex_pb2_grpc.MutexCommunicator):
    def __init__(self, name, nodes, task):
        super().__init__()
        self.name = name
        self.delay = 5
        self.nodes = nodes
        self.request_pending = set()
        self.msg_queue = queue()
        self.task = task
        self.init()

    def init(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        mutex_pb2_grpc.add_MutexCommunicatorServicer_to_server(MediaProvider(), server)
        server.add_insecure_port(ip_address)
        server.start()
        logging.info(f"Mutex provider started at {ip_address} ###############.")
        server.wait_for_termination()
        
    def message(self, request, context):
        if request.msg_type == 'request':
            print('requesting message to others')
        elif request.msg_type == 'response':
            print('processing response message')
        return 
    
    def run(self):
        # send message to all.
        self.request_cs()
        
        # ensure all the response msgs are recieved or wait.
        self.ensure_all_response()
        
        #excute the task.
        self.task()
        
        # handle queued messages.
        self.handle_queued_message()
        return 
        
    def send_msg(self, node):
        with grpc.insecure_channel(node.address) as channel:
            stub = mutex_pb2_grpc.MutexCommunicatorStub(channel)
            response = stub.message(MessageRequest(name=node.id))
            print(f"Response: {response.content}")
        return
    
    def request_cs(self):
        for node in self.nodes:
            self.send_msg(node, MessageRequest())
            self.request_pending.add(node)
    
    def ensure_all_response(self):
        while True:
           if self.request_pending:
               time.sleep(self.delay)
           else:
               self.execute_the_tasks()

    def handle_queued_message(self):
        # msg = self.msg_queue.get()
        # while msg != None :
        #     msg = self.msg_queue.
        #     self.send_msg()
        return
