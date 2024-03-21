import grpc
from server_pb2_grpc import MediaLibraryStub
from server_pb2 import PublishRequest
from file_manager import FileManager
import socket

def main():
    # Get IP address
    ip = socket.gethostbyname(socket.gethostname())
    port_number= 6100
    ip_address= f"{ip}:{port_number}"

    print("########## This is a Provider Terminal ###################")
    print(f"Content Provider connected to server at at {ip_address}")

    # Initialize gRPC channel and stub
    channel = grpc.insecure_channel(ip_address)
    stub = MediaLibraryStub(channel)

    # Folder path for files to be published
    folder_path = "storage//provider"

    while True:
        print("Following content files are ready to be published:")
        FileManager.list_all_files_in_folder(folder_path)

        while True:
            # Prompt user for file to publish
            file_name = input("Which file would you like to share with Servers? (Enter 'exit' to quit) ")
            if file_name.lower() == 'exit':
                break        

            # Check if the file exists
            if FileManager.file_exists(folder_path, file_name):
                break
            else:
                print(f"File '{file_name}' not found in the content provider folder. Please try again.")

        if file_name.lower() == 'exit':
            break

        # Read the content of the file
        content = FileManager.read_file_content(folder_path, file_name)

        # Create request to publish content
        request = PublishRequest(file_name=file_name, file_content=content)

        try:
            # Send request to server
            response = stub.publishContent(request)
            print(response)
        except grpc.RpcError as e:
            print(f"Error occurred during gRPC communication: {e}")
        except Exception as e:
            print(f"Unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
