from concurrent import futures
import logging
import grpc
import mutex_pb2_grpc
from mutex_pb2 import MutexResponse
import socket

ip = socket.gethostbyname(socket.gethostname())
port_number = 6100
ip_address = f"{ip}:{port_number}" 

node_id = 'p1'
time_stamp = 1

class MutexManager(mutex_pb2_grpc.MutexCommunicator):
    def __init__(self, nodes, node_id):
        nodes = nodes
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        mutex_pb2_grpc.add_MutexCommunicatorServicer_to_server(MutexManager(), server)
        server.add_insecure_port(ip_address)
        server.start()
        logging.info(f"Mutex communicator started at {ip_address} ###############.")
        server.wait_for_termination()
    
    def request_cs(self, request, context):
        # Reply only if if the current node is not using cs.
        # or the current time stamp is greater than requesting node time stamp.
        return MutexResponse()
    
    def request_cs_and_run_task(self, task):
        count = 0
        # use multi threading in this case.
        for node in range(self.nodes):
            with grpc.insecure_channel(node.address) as channel:
                stub = mutex_pb2_grpc.MutexCommunicatorStub(channel)
                response = stub.request_cse(mutex_pb2_grpc.MutexRequest(name=node_id))
                count += 1
                print(f"Response: {response.content}")
        task()
        
                
    