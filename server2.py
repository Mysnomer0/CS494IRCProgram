import socket
import select

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

# Setup the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Make sure we can reuse sockets
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Bind our IP and port to the socket
server_socket.bind((IP, PORT))
# Start listening
server_socket.listen()
# This list will contain all of the sockets we have a connection to
sockets_list = [server_socket]

# List of connected clients, socket as a key, user header and name as data
clients = {}

# List of rooms, string as a key, client names as data
rooms = {}

print(f'Listening for connections on {IP}:{PORT}...')

# Receive and process messages from this socket
def receive_message(client_socket):

    try:
        # Get the message header that is alwasy sent first
        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False
        # Get the length of the message
        message_length = int(message_header.decode('utf-8').strip())
        # Return the message formatted as an object
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        return False

# Continually loop through to read and process messages
while True:

    # Get the list of sockets
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    # Go through the list of sockets
    for notified_socket in read_sockets:
        # If the server socket was notified
        if notified_socket == server_socket:
            # Accept this new socket connection and add the client
            client_socket, client_address = server_socket.accept()
            # The user should send it's username first, so be sure to receive it
            user = receive_message(client_socket)

            if user is False:
                continue

            sockets_list.append(client_socket)
            # Add this client to the list
            clients[client_socket] = user

            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))
        # Otherwise, process received messages
        else:
            # Get the message
            message = receive_message(notified_socket)
            # Gracefully close the connection if the message failed
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
                # Remove the socket from the list of connections
                sockets_list.remove(notified_socket)
                # Remove the client from the list
                del clients[notified_socket]

                continue
            # Get the user who sent this message
            user = clients[notified_socket]

            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            # Process the received message to check for commands

            # If the user asked to create a room
            if message['data'].decode("utf-8").split()[0] == '/create' and message['data'].decode("utf-8").split()[1] == 'room':
                # Allocate the space in the rooms array for the list of clients in that room
                rooms[message['data'].decode("utf-8").split()[2]] = []
                # Tell the user that they created the room

                # Build the reply
                serverUsername = 'Server'
                serverUsername = serverUsername.encode('utf-8')
                serverUsernameHeader = f"{len(serverUsername):<{HEADER_LENGTH}}".encode('utf-8')
                reply = 'You created the room ' + message['data'].decode("utf-8").split()[2]
                reply = reply.encode('utf-8')
                replyHeader = f"{len(reply):<{HEADER_LENGTH}}".encode('utf-8')

                notified_socket.send(serverUsernameHeader + serverUsername + replyHeader + reply)

                print ('Created room ' + message['data'].decode("utf-8").split()[2])
            # If the user asked to be added to a room
            elif message['data'].decode("utf-8").split()[0] == '/join' and message['data'].decode("utf-8").split()[1] == 'room':
                # Make sure the room exists
                if message['data'].decode("utf-8").split()[2] not in rooms:
                    continue
                # If the user isn't already in that room
                if user["data"].decode("utf-8") not in rooms[message['data'].decode("utf-8").split()[2]]:
                    # Add them to the room
                    rooms[message['data'].decode("utf-8").split()[2]].append(user["data"].decode("utf-8"))
                else:
                    continue
                # Tell the user that they created the room

                # Build the reply
                serverUsername = 'Server'
                serverUsername = serverUsername.encode('utf-8')
                serverUsernameHeader = f"{len(serverUsername):<{HEADER_LENGTH}}".encode('utf-8')
                reply = 'You have been added to room ' + message['data'].decode("utf-8").split()[2]
                reply = reply.encode('utf-8')
                replyHeader = f"{len(reply):<{HEADER_LENGTH}}".encode('utf-8')

                notified_socket.send(serverUsernameHeader + serverUsername + replyHeader + reply)

                print ('Added ' + user["data"].decode("utf-8") + ' to room ' + message['data'].decode("utf-8").split()[2])
                print('The room now contains these clients: ' + str(rooms[message['data'].decode("utf-8").split()[2]]))
            # If the user asked to be removed to a room
            elif message['data'].decode("utf-8").split()[0] == '/leave' and message['data'].decode("utf-8").split()[1] == 'room':
                # Make sure the room exists
                if message['data'].decode("utf-8").split()[2] not in rooms:
                    continue
                print('got here 1')
                # If the user is in that room
                if user["data"].decode("utf-8") in rooms[message['data'].decode("utf-8").split()[2]]:
                    # Remove them to the room
                    rooms[message['data'].decode("utf-8").split()[2]].remove(user["data"].decode("utf-8"))
                else:
                    continue
                print('got here 2')
                # Tell the user

                # Build the reply
                serverUsername = 'Server'
                serverUsername = serverUsername.encode('utf-8')
                serverUsernameHeader = f"{len(serverUsername):<{HEADER_LENGTH}}".encode('utf-8')
                reply = 'You have left room ' + message['data'].decode("utf-8").split()[2]
                reply = reply.encode('utf-8')
                replyHeader = f"{len(reply):<{HEADER_LENGTH}}".encode('utf-8')

                notified_socket.send(serverUsernameHeader + serverUsername + replyHeader + reply)

                print ('Removed ' + user["data"].decode("utf-8") + ' from room ' + message['data'].decode("utf-8").split()[2])
                print('The room now contains these clients: ' + str(rooms[message['data'].decode("utf-8").split()[2]]))
            # Otherwise, send this message to all clients in the same rooms
            else:
                # Loop through each room
                for roomName in rooms:
                    # If the client is in this room
                    if user["data"].decode("utf-8") in rooms[roomName]:
                        # Go through all the clients in this room and send them the message
                        # For each socket
                        for clientSocket in sockets_list:
                            # Make sure  the data key is there
                            if clientSocket in clients and 'data' in clients[clientSocket]:
                                # If this socket's client shows up in this room
                                if clients[clientSocket]['data'].decode('utf-8') in rooms[roomName]:
                                    # Send this client the message
                                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

                #for client_socket in clients:
                #    if client_socket != notified_socket:
                #        client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    # Clean up the sockets when we get exceptions
    for notified_socket in exception_sockets:

        sockets_list.remove(notified_socket)

        del clients[notified_socket]
        