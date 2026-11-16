# Client code
import socket
import sys
import os
from common import *


# Name and port number of the server to
# which want to connect.

def ControlChannel(serverName, serverPort):
    # serverName = "ecs.fullerton.edu"
    # serverPort = 12000

    # Create a socket
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Get the ip from a domain Name 
    try: 
        hostIP = socket.gethostbyname(serverName) 
    except socket.gaierror: 

        # this means could not resolve the host 
        print ("there was an error resolving the host")
        sys.exit() 

    # connecting to the server with IPs
    try:
        clientSocket.connect((hostIP, serverPort)) 
    except socket.error as e:
        print("Error connecting to server:", e)
        sys.exit(1)
    # or with server name
    # clientSocket.connect((serverName , serverPort))

    return clientSocket

# Client listens on ephemeral port, server connects to it
def DataChannel():

    # Create a socket
    dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to port 0
    dataSocket.bind(('',0))
    dataSocket.listen(1)

    # Retreive the ephemeral port number
    return dataSocket

# Runs one ls / get / put on server using a fresh data channel from client
def Transfer(clientSocket, cmd, fileName=None):
    if cmd == "put" and not os.path.isfile(fileName):
        print("local file not found")
        return
    
    dataSocket = DataChannel()
    port = dataSocket.getsockname()[1]

    # Tell the server the command and which port we are listening on
    if fileName:
        send_msg(clientSocket, cmd + " " + fileName + " " + str(port))
    else:
        send_msg(clientSocket, cmd + " " + str(port))

    status = recv_msg(clientSocket).decode()
    if status != "OK":
        print(status)
        dataSocket.close()
        return

    connSocket, _ = dataSocket.accept()

    if cmd == "put":
        with open(fileName, "rb") as fileObj:
            data = fileObj.read()
        send_msg(connSocket, data)
    else:
        data = recv_msg(connSocket)
        if cmd == "ls":
            print(data.decode())
        else: # get
            with open(fileName, "wb") as fileObj:
                fileObj.write(data)

    # Tear down the data channel after every transfer
    connSocket.close()
    dataSocket.close()

    if cmd != "ls":
        recv_msg(clientSocket)
        print(fileName, ":", len(data), "bytes transferred")
    
def main():
    if len(sys.argv) != 3:
        print("Error: Please provide 2 arguments")
        sys.exit(1)

    user_args = sys.argv[1:]

    serverName = user_args[0]
    serverPort = int(user_args[1])
    clientSocket = ControlChannel(serverName, serverPort)

    while 1:
        parts = input("ftp> ").split()
        if not parts:
            continue

        if parts[0] == "quit":
            clientSocket.close()
            break
        elif parts[0] == "ls" and len(parts) == 1: # ls <directory> is not supported
            Transfer(clientSocket, "ls")
        elif parts[0] in ("get", "put") and len(parts) == 2:
            Transfer(clientSocket, parts[0], parts[1])
        else:
            print("commands: get <file>, put <file>, ls, quit")

main()