:: Delete Existing grpc files if exists.
del .\ott\*_pb2*.py

:: Generate new grpc files based on proto file provided.
python -m grpc_tools.protoc -I .\ott\protobufs  --python_out=.\ott --grpc_python_out=.\ott .\ott\protobufs\server.proto



