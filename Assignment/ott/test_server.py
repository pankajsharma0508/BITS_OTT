import unittest
# from concurrent import futures
# import grpc
# from Assignment.ott.server import MediaLibraryService
# from server_pb2_grpc import MediaLibraryStub, server_pb2_grpc
# from server_pb2 import ContentRequest, server_pb2

class TestServer(unittest.TestCase):
    # def setUp(self):
    #     self.server = grpc.server(futures.ThreadPoolExecutor())
    #     server_pb2_grpc.add_MediaLibraryServicer_to_server(MediaLibraryService(), self.server)
    #     self.server.add_insecure_port("[::]:50051")
    #     self.server.start()

    # def tearDown(self):
    #     self.server.stop(None)

    def testHello(self):
        pass
        # with grpc.insecure_channel("localhost:50051") as channel:
        #     stub = MediaLibraryStub(channel)
        #     response = stub.getContent(server_pb2.getContent(ContentRequest(file_name='test.mp4')))
        #     print(response)
        #     self.assertEqual(response.message, "Hello, Alice!")

if __name__ == '__main__':
    unittest.main()