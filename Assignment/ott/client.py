import grpc
from server_pb2_grpc import MediaLibraryStub
from server_pb2 import ContentRequest
from file_manager import FileManager
import socket

def main():
    # Get IP addresaa
    ip = socket.gethostbyname(socket.gethostname())
    port_number= 6100
    ip_address= f"{ip}:{port_number}"

    print("########## This is a client Terminal ###################")
    print(f"Content Client connected to server at at {ip_address}")

    # Initialize gRPC channel and stub
    channel = grpc.insecure_channel(ip_address)
    stub = MediaLibraryStub(channel)

    # Folder path for saving files on the client side
    folder_path = "storage//client"

    # Main loop to prompt user for file name
    while True:
        file_name = input("Which media file would you like to search? (Enter 'exit' to quit) ")
        if file_name.lower() == 'exit':
            break

        # Check if file already exists locally
        if FileManager.file_exists(folder_path, file_name):
            print(f"File '{file_name}' already exists locally.")
            open_in_browser = input("Do you want to open it? (yes/no) ")
            if open_in_browser.lower() == 'yes':
                FileManager.open_media_file_in_browser(folder_path, file_name)
            continue

        # Create request with the file name
        request = ContentRequest(file_name=file_name,client_ip = ip_address)

        try:
            # Send request to server
            metadata = [('visited', '')]
            response = stub.getContent(request, metadata=metadata)
            # Check response status
            if response.status == 200:                
                print(f'File present on server {response.server_ip} start to download. Requesting server to transfer file to client {ip_address}')
                FileManager.save_file_content(folder_path, file_name, response.file_content)
                FileManager.open_media_file_in_browser(folder_path, file_name)
            else:
                print(f"File '{file_name}' not found on the server.")
        except grpc.RpcError as e:
            print(f"Error occurred during gRPC communication: {e}")
        except Exception as e:
            print(f"Unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
