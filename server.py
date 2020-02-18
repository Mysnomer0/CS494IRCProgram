# Milan Mauck

from room import Room
from client import Client
import sys
import socket
import select

class Server:
    def __init__(self):
        self.listOfRooms = []
        self.listOfClients = []
        self.host = '' 
        self.socketList = []
        self.receiveBuffer = 4096 
        self.port = 9090

    def StartServer(self):
        
        # Setup the server socket
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind((self.host, self.port))
        serverSocket.listen(10)
    
        # Add the server socket object to the list of readable connections
        self.socketList.append(serverSocket)
    
        print("Server started on port " + str(self.port))
    
        # Continuously listen for new connections
        while True:

            # get the list sockets which are ready to be read through select
            # 4th arg, time_out  = 0 : poll and never block
            isReadyToRead,isReadyToWrite,inError = select.select(self.socketList,[],[],0)
        
            # Check for any new connection requests
            for sock in isReadyToRead:
                # If a new connection request recieved
                if sock == serverSocket: 
                    # Accept the new connection
                    socketForward, address = serverSocket.accept()
                    # Add this socket to the list of connected
                    self.socketList.append(socketForward)
                    print('Client with address ' + str(address) + ' connected!')
                    
                    self.Broadcast(serverSocket, socketForward, "[%s:%s] entered room\n" % address)
                
                # Otherwise, process a message from a client
                else:
                    try:
                        # Get the data from the socket
                        data = sock.recv(self.receiveBuffer)
                        # If there actually is data
                        if data:
                            # self.Broadcast the message
                            self.Broadcast(serverSocket, sock, "\r" + '[' + str(sock.getpeername()) + '] ' + data)  
                        else:
                            # Otherwise, the connection is broken, so remove the socket from the list
                            if sock in self.socketList:
                                self.socketList.remove(sock)

                            # Tell everyone the client disconnected
                            self.Broadcast(serverSocket, sock, "Client (%s, %s) is offline\n" % address) 

                    # Tell everyone the client disconnected
                    except:
                        self.Broadcast(serverSocket, sock, "Client (%s, %s) is offline\n" % address)
                        continue

        serverSocket.close()
        
    # Sends the given message to all connected clients
    def Broadcast(self, serverSocket, sock, message):
        for socket in self.socketList:
            # Make sure we're sending the message to the right socket
            if socket != serverSocket and socket != sock :
                # Try to send the message
                try :
                    socket.send(message)
                # If it fails, we have a broken connection
                except :
                    socket.close()
                    if socket in self.socketList:
                        self.socketList.remove(socket)
 
if __name__ == "__main__":

    # Create a server
    server = Server()
    # Start the server listening
    sys.exit(server.StartServer()) 