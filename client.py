import sys
import socket
import select

class Client:
    def __init__(self, name, host, port):
        self.name = name
        self.host = host
        self.port = port
        self.exit = False

        # Get the socket isntance
        currentSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        currentSocket.settimeout(2)
        
        # Try to connect to the host
        try:
            currentSocket.connect((self.host, self.port))
        except :
            print('Can\'t connect.')
            return
        
        # Clear the standard out
        print('Connected!')
        sys.stdout.write('[Me] ')
        sys.stdout.flush()
        print('Starting loop')
        # While we're connected, listen on the socket
        while not self.exit:
            # Get the socket list
            socketList = [sys.stdin, currentSocket]
            # Get the list sockets which are readable
            readyToRead,readyToWrite,inError = select.select(socketList , [], [])
            # Go through all the sockets
            for sock in readyToRead:
                # If we're on the server's socket   
                if sock == currentSocket:
                    # Get the data from the received message
                    data = sock.recv(4096)
                    # If the data is nonexistent, this means we've been disconnected
                    if not data:
                        print('\nDisconnected from server')
                        self.exit = True
                        break
                    # Otherwise, output the received data
                    else:                    
                        sys.stdout.write(data)
                        sys.stdout.write('[Me] ')
                        sys.stdout.flush()     
                # Otherwise, read the input
                else:
                    # user entered a message
                    message = sys.stdin.readline()
                    currentSocket.send(message)
                    sys.stdout.write('[Me] ')
                    sys.stdout.flush()


if __name__ == '__main__':
    
    # Parse the arguments
    while True:
        if input('Would you like to create a new connection? (y/n) ') == 'n':
            break
        # Create the client with the new connection
        client = Client(input('What is your name? '), input('What host would you like to connect to? '), int(input('What port would you like to connect to? ')))

