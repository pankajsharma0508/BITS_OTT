import grpc
from mutex_manager import MutexManager
from communicator import Communicator
from server_pb2_grpc import MediaLibraryStub
from server_pb2 import PublishRequest
from file_manager import FileManager
import socket

folder_path = "storage//provider"


class ContentProvider:
    def __init__(self):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port_number = 6100  # input("Please Enter the port_number")  # 6100
        self.communicator = Communicator(
            self.ip, self.port_number, msg_handler=self.msg_handler
        )
        # self.start_rpc()
        self.init_user_interface()

    def start_rpc(self):
        channel = grpc.insecure_channel(f"{self.ip}:{self.port_number}")
        self.media_library = MediaLibraryStub(channel)

    def init_user_interface(self):
        print("########## This is a Provider Terminal ###################")
        print(f"Content Provider started at {self.ip}:{self.port_number}")

        while True:
            print("Following content files are ready to be published:")
            FileManager.list_all_files_in_folder(folder_path)

            while True:
                # Prompt user for file to publish
                file_name = input(
                    "Enter file name to share with Servers? (Enter 'exit' to quit) "
                )
                if file_name.lower() == "exit":
                    break

                self.publish_content(file_name=file_name)

    def handle_user_request(self):
        mutex_manager = MutexManager()

    def publish_content(self, file_name):
        try:
            # Read the content of the file
            content = self.read_file_if_exists(file_name)

            # Create request to publish content
            request = PublishRequest(file_name=file_name, file_content=content)
            response = self.media_library.publishContent(request)
            print(response)

        except grpc.RpcError as e:
            print(f"Error occurred during gRPC communication: {e}")
        except Exception as e:
            print(f"Unexpected error occurred: {e}")

    def read_file_if_exists(self, file_name):
        # Check if the file exists
        if FileManager.file_exists(folder_path, file_name) is False:
            Exception(f"File '{file_name}' not found in the content provider folder.")
        return FileManager.read_file_content(folder_path, file_name)

    def msg_handler(message, clientAddress):
        print("Message from ", clientAddress, ": ", message)


if __name__ == "__main__":
    cdn = ContentProvider()
