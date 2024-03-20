from concurrent import futures
import grpc
import server_pb2_grpc
from server_pb2 import PublishResponse, ContentResponse,ContentRequest,FileResponse, FileRequest 
from file_manager import FileManager
import logging
from Node import ServerLinkedList

media_library = list()
ip_address = 'localhost:5100'
replica_servers_address = 'localhost:6100,'
folder_path = "storage//server"

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

server_list = ServerLinkedList(replica_servers_address)
server_list.display()
class MediaLibraryService(server_pb2_grpc.MediaLibraryServicer):

    def __init__(self):
        self.visited_ips = {}  # Dictionary to maintain visited IP addresses

    def getContent(self, request, context):
        logging.info(f"Request from client {request.client_ip} to serve file => {request.file_name}")

        if request.file_name in media_library:
            logging.info(f'File {request.file_name} on local server {ip_address} starting to download')
            content = FileManager.read_file_content(folder_path, request.file_name)
            if content:
                logging.info(f'File {request.file_name} downloaded successfully')
                print(f'update local media library with file {request.file_name}')
                media_library.append(request.file_name)
                return ContentResponse(file_content=content, status=200, server_ip=ip_address)

        print(f"File not found locally on current server {ip_address} attempting to retrieve file from other servers")
        self.visited_ips[ip_address] = True
        response = self.retrieve_file_from_other_servers(request)
        if response:
            return response

        # Log file not found as a warning
        logging.warning(f'File {request.file_name} not found on any server')
        return ContentResponse(file_content=b'', status=404, server_ip=ip_address)
    
    def retrieve_file_from_other_servers(self, request):      
        file_found = False  
        current = server_list.head
        while current:
            ip = current.ip
            #cost = current.cost
            if ip != ip_address and ip not in self.visited_ips:  # Check if IP hasn't been visited
                logging.info(f'Connecting to remote server {ip} for file {request.file_name}')
                try:
                    channel = grpc.insecure_channel(ip)
                    stub = server_pb2_grpc.MediaLibraryStub(channel)
                    c_request = ContentRequest(file_name=request.file_name, client_ip=ip)
                    c_response = stub.getContent(c_request)
                    if c_response.status == 200:
                        logging.info(f'File found on server {ip}, retrieving file {request.file_name}')
                        FileManager.save_file_content(folder_path, request.file_name, c_response.file_content)
                        self.visited_ips[ip] = True  # Mark IP as visited
                        file_found = True
                        return c_response
                except grpc.RpcError as e:
                    logging.error(f"Error connecting to server {ip}: {e}")
                except Exception as e:
                    logging.error(f"Unexpected error occurred: {e}")
            current = current.next

        if not file_found:
            logging.info(f'File {request.file_name} not found on any server.')
        
        return ContentResponse(file_content=b'', status=404, server_ip=ip_address)

    def check_file_Exists_other_servers(self, request):
        for ip, cost in sorted(server_list.items(), key=lambda x: x[1]):
            logging.info(f'Connecting to remote server {ip} for file {request.file_name}')
            try:
                channel = grpc.insecure_channel(ip)
                stub = server_pb2_grpc.MediaLibraryStub(channel)
                response = stub.checkFileExists(request.file_name , request.client_ip)
                if response.status == 200:
                    logging.info(f'File found on server {ip}, retrieving file {request.file_name}')
                    return response
            except grpc.RpcError as e:
                logging.error(f"Error connecting to server {ip}: {e}")
            except Exception as e:
                logging.error(f"Unexpected error occurred: {e}")

        return None

    def publishContent(self, request, context):
        logging.info(f"Received File from content provider to be stored on server: {request.file_name}")
        FileManager.save_file_content(folder_path, request.file_name, request.file_content)
        media_library.append(request.file_name)
        return PublishResponse(response="done")


if __name__ == '__main__':
    # Start gRPC server
    #ip_address = input("Enter  server IP address with port (e.g., localhost:5100): ")
    #replica_servers_address = input("Enter comma seprated lis tof IP addresses with port  for nearest servers (e.g., localhost:5100,localhost:6100) ")
    local_File=FileManager.list_all_files_in_folder(folder_path)

    for file in local_File:
        media_library.append(file)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server_pb2_grpc.add_MediaLibraryServicer_to_server(MediaLibraryService(), server)
    server.add_insecure_port(ip_address)
    server.start()
    logging.info("Media library service started successfully, ready for clients to serve files.. ")
    server.wait_for_termination()
