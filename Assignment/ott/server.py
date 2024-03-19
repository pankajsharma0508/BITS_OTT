from concurrent import futures
import grpc
import server_pb2_grpc
from server_pb2 import PublishResponse, ContentResponse,ContentRequest,FileResponse, FileRequest 
from file_manager import FileManager
import logging

media_library = list()
ip_address = '172.31.15.9:6100'
folder_path = "storage//server"
server_list = {'172.31.2.98:5100': 1, '172.31.15.9:6100': 2, }

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


class MediaLibraryService(server_pb2_grpc.MediaLibraryServicer):

    def getContent(self, request, context):
        logging.info(f"Request from client {request.client_ip} to serve file => {request.file_name}")

        if request.file_name in media_library:
            logging.info(f'File {request.file_name} on local server {ip_address} starting to download')
            content = FileManager.read_file_content(folder_path, request.file_name)
            if content:
                logging.info(f'File {request.file_name} downloaded successfully')
                print(f'update local media library with file {request.file_name}')
                media_library.append(request.file_name)
                return ContentResponse(file_content=content, status=200, server_ip = ip_address)

        print(f"File not found locally on current server {ip_address} attempting to retrieve file from other servers");

        response = self.retrieve_file_from_other_servers(request)
        if response:
            return response

        # Log file not found as a warning
        logging.warning(f'File {request.file_name} not found on any server')
        return ContentResponse(file_content=b'', status=404, server_ip = ip_address)
    
    def checkFileExists(self, request, context):         
         if request.file_name in media_library:
             return FileResponse(status=200, server_ip = ip_address)         
         else:         
            print(f"File {request.file_name} not found locally on current server {ip_address} attempting to retrieve file from other servers");
            response = self.check_file_Exists_other_servers(FileRequest(file_name=request.file_name,client_ip = ip_address))
            if response:            
                return response
            # Log file not found as a warning
            logging.warning(f'File {request.file_name} not found on  server {response.server_ip}')
            return FileResponse(server_ip=response.server_ip, status=404)

    def retrieve_file_from_other_servers(self, request):
        for ip, cost in sorted(server_list.items(), key=lambda x: x[1]):
            if ip != ip_address:            
                logging.info(f'Connecting to remote server {ip} for file {request.file_name}')
                try:
                    channel = grpc.insecure_channel(ip)
                    stub = server_pb2_grpc.MediaLibraryStub(channel)
                    c_request = ContentRequest( file_name=request.file_name, client_ip =ip)
                    c_response = stub.getContent(c_request)                    
                    if c_response.status == 200:
                        logging.info(f'File found on server {ip}, retrieving file {request.file_name}')
                        FileManager.save_file_content(folder_path , request.file_name, c_response.file_content);
                        return c_response
                except grpc.RpcError as e:
                    logging.error(f"Error connecting to server {ip}: {e}")
                except Exception as e:
                    logging.error(f"Unexpected error occurred: {e}")

        return ContentResponse(file_content=b'', status=404, server_ip = ip)
    
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


def serve():
    #ip_address = input("Enter content provider IP address with port (e.g., localhost:5100): ")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server_pb2_grpc.add_MediaLibraryServicer_to_server(MediaLibraryService(), server)
    server.add_insecure_port(ip_address)
    server.start()
    logging.info("Media library service started successfully, ready for clients to serve files.. ")

    server.wait_for_termination()


if __name__ == '__main__':
    serve()
