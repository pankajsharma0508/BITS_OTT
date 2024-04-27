import json
import grpc
from hash_manager import HashManager
from data_structures import MutexMessage, MutexNode
from mutex_manager import MutexManager
from communicator import Communicator
from server_pb2_grpc import MediaLibraryStub
from server_pb2 import PublishRequest
from file_manager import FileManager

folder_path = "storage//provider"
mutex_threads = dict()


class ContentProvider:
    def __init__(self):
        self.init_node_data()
        self.communicator = Communicator(
            self.node.ip, self.node.port, msg_handler=self.msg_handler
        )

        self.init_user_interface()
        # self.start_rpc()
        return

    def init_node_data(self):
        name = input("Please Enter the node name: ")
        self.other_nodes = list()

        with open("data.json", "r") as settings:
            config = json.loads(settings.read())

            # read server configuration
            server = config["server"]
            self.server_ip = server["ip"]
            self.server_port = server["port"]

            # read provider configuration
            providers = list(config["providers"])
            for index, node in enumerate(providers):
                providerNode = MutexNode(
                    ip=node["ip"], port=node["port"], name=node["name"]
                )
                if node["name"] == name:
                    self.node = providerNode
                else:
                    self.other_nodes.append(providerNode)

    def start_rpc(self):
        channel = grpc.insecure_channel(f"{self.server_ip}:{self.server_port}")
        self.media_library = MediaLibraryStub(channel)

    def init_user_interface(self):
        print("########## This is a Provider Terminal ###################")
        print(f"Provider ({self.node.name}) started at {self.node.ip}:{self.node.port}")

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
                content = FileManager.read_file_content(
                    folder_path=folder_path, file_name=file_name
                )

                print(f"Calculating File hash for {file_name}.")
                file_hash = HashManager.calculate_hash(file_content=content)
                self.handle_user_request(file_name=file_name, file_hash=file_hash)

    def handle_user_request(self, file_name, file_hash):
        mutex_thread = MutexManager(
            communicator=self.communicator,
            node=self.node,
            other_nodes=self.other_nodes,
            task=self.publish_content,
            file_name=file_name,
            file_hash=file_hash,
        )
        mutex_thread.start()
        # will replace file_name with hash
        mutex_threads[file_hash] = mutex_thread
        print(file_hash)

    def publish_content(self, file_name):
        print(f"publish_content: {file_name}")
        return
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

    def msg_handler(self, message, clientAddress):
        # response type: read the target from the msg
        # look for the thread send message to handle.

        mutex_thread = mutex_threads.get(message.file_hash)
        if mutex_thread:
            mutex_thread.handle_message(msg=message)
        else:
            print(f"Request msg revd => CS is not used. \n {message.node.to_json()}")
            reply = MutexMessage(
                type=2,
                node=self.node,
                file_name=message.file_name,
                file_hash=message.file_hash,
                timestamp=0,
            )
            self.communicator.send_msg(message.node, reply)
            print(f"Reply Message Send. \n {reply.node.to_json()}")


if __name__ == "__main__":
    cdn = ContentProvider()
