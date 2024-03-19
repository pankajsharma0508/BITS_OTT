pip install grpcio 
pip install grpcio-tools
1. Server should search for the request file in the local database. If available then return the file.
2. If the file is not available forward the request to next closest server. This can be cyclic.
3. Once the file found on the server, it should return the file to server. 
4. If the file is not found should return appropriate message.
 