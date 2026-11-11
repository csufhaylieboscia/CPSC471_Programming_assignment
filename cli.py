# Client code
import socket
import sys



# Name and port number of the server to
# which want to connect.

def ControlChannel(serverName, serverPort):
    # serverName = "ecs.fullerton.edu"
    # serverPort = 12000

    # Create a socket
    clientSocket = socket.socket(socket.AF_INET, socket.SOCKSTREAM)

    # Get the ip from a domain Name 
    try: 
        hostIP = socket.gethostbyname(serverName) 
    except socket.gaierror: 

        # this means could not resolve the host 
        print ("there was an error resolving the host")
        sys.exit() 

    # connecting to the server with IP
    clientSocket.connect((hostIP, serverPort)) 
    # or with server name
    # clientSocket.connect((serverName , serverPort))

    return clientSocket

    
def DataChannel(serverAddr, fileName):

    # Create a socket
    dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to port 0
    dataSocket.bind(('',0))

    # Retreive the ephemeral port number
    print( "I chose ephemeral port: ", dataSocket.getsockname()[1]
    )

    dataSocket.connect((ServerAddr, dataSocket.getsockname()[1] ))

    # A string we want to send to the server
    # data = 'Hello world! This is a very long string.'

    fileObj = open(fileName, "r")


    bytesSent = 0

    # Keep sending bytes until all bytes are sent
    while bytesSent != len(data):

        # Send that string!
        bytesSent += dataSocket.send(data[bytesSent:])

    # Close the socket
    dataSocket.close()

def main():
    if len(sys.argv) != 3:
        print("Error: Please provide 2 arguments")
        sys.exit(1)

    user_args = sys.argv[1:]

    serverName = user_args[0]
    serverPort = user_args[1]

