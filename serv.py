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
                send_msg(connectionSocket, "OK")
                dataSocket = DataChannel(addr[0], int(args[0]))
                send_msg(dataSocket, "\n".join(os.listdir(".")))
                dataSocket.close()
            elif cmd == "get":
                fileName = os.path.basename(args[0])
                if not os.path.isfile(fileName):
                    send_msg(connectionSocket, "ERR file not found")
                    raise FileNotFoundError(fileName)
                send_msg(connectionSocket, "OK")
                dataSocket = DataChannel(addr[0], int(args[1]))
                with open(fileName, "rb") as fileObj:
                    send_msg(dataSocket, fileObj.read())
                dataSocket.close()
            elif cmd == "put":
                fileName = os.path.basename(args[0])
                send_msg(connectionSocket, "OK")
                dataSocket = DataChannel(addr[0], int(args[1]))
                data = recv_msg(dataSocket)
                dataSocket.close()
                with open(fileName, "wb") as fileObj:
                    fileObj.write(data)
            else:
                send_msg(connectionSocket, "ERR unknown command")
                raise ValueError("unknown command " + cmd)

            print(cmd, "SUCCESS")
        except Exception as e:
            print(cmd, "FAILURE:", e)
            
    connectionSocket.close()