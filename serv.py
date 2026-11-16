# Server code
import socket
import sys
import os
from common import *

def DataChannel(clientIP, clientPort):
    dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dataSocket.connect((clientIP, clientPort))
    return dataSocket

# The port on which to listen
if len(sys.argv) != 2:
    sys.exit("usage: python serv.py <PORT NUMBER>")
serverPort = int(sys.argv[1])

# Create a TCP socket
serverSocket = socket.socket(socket.AF_INET ,socket.SOCK_STREAM)

# Bind the socket to the port
serverSocket.bind(('', serverPort))

# Start listening for incoming connections
serverSocket.listen(1)
print("The Server is ready to receive")

# Forever accept incoming connections
while 1:
    # Accept a connection and get client’s socket
    connectionSocket , addr = serverSocket.accept()
    print("Client connected:", addr)

    # Keep processing commands until the client disconnects
    while 1:
        try:
            request = recv_msg(connectionSocket).decode().split()
        except ConnectionError:
            # The other side closed its socket (quit)
            break

        cmd, args = request[0], request[1:]
        try:
            if cmd == "ls":
                if len(args) != 1:
                    raise ValueError("Invalid ls argument")
                send_msg(connectionSocket, "OK")
                dataSocket = DataChannel(addr[0], int(args[0]))
                send_msg(dataSocket, "\n".join(os.listdir(".")))
                dataSocket.close()
            elif cmd == "get":
                if len(args) != 2:
                    raise ValueError("Invalid get arguments")
                fileName = os.path.basename(args[0])
                if not os.path.isfile(fileName):
                    send_msg(connectionSocket, "ERR file not found")
                    raise FileNotFoundError(fileName)
                send_msg(connectionSocket, "OK")
                dataSocket = DataChannel(addr[0], int(args[1]))
                byteCount = 0
                with open(fileName, "rb") as fileObj:
                    while 1:
                        data = fileObj.read(4096)
                        if not data:
                            break
                        dataSocket.sendall(data)
                        byteCount += len(data)
                dataSocket.close()
                send_msg(connectionSocket, f"Done {fileName} {byteCount}")
            elif cmd == "put":
                if len(args) != 2:
                    raise ValueError("Invalid put arguments")
                fileName = os.path.basename(args[0])
                send_msg(connectionSocket, "OK")
                dataSocket = DataChannel(addr[0], int(args[1]))
                data = recv_msg(dataSocket)
                byteCount = 0
                with open(fileName, "wb") as fileObj:
                    while 1:
                        data = dataSocket.recv(4096)
                        if not data:
                            break
                        fileObj.write(data)
                        byteCount += len(data)
                dataSocket.close()
                send_msg(connectionSocket, f"Done {fileName} {byteCount}")
            else:
                send_msg(connectionSocket, "ERR unknown command")
                raise ValueError("unknown command " + cmd)

            print(cmd, "SUCCESS")
        except Exception as e:
            print(cmd, "FAILURE:", e)
            
    connectionSocket.close()