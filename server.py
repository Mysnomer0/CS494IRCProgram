# Milan Mauck

from flask import *
from room import Room
from client import Client


# Create the server as an HTTP app
app = Flask('CS494IRCServer')

# The list of rooms
listOfRooms = []
# The list of clients
listOfClients = []

# The list rooms command
@app.route('/rooms', methods=['POST'])
def ListRooms():
    if request.method == 'POST':
        listOfRoomsAsString = ''
        for i in range(len(listOfRooms)):
            listOfRoomsAsString += listOfRooms[i].name
        return listOfRoomsAsString

# The list rooms command
@app.route('/connect', methods=['POST'])
def ListRooms():
    if request.method == 'POST':
        # Add this client to the list
        listOfClients.append(Client(''))

# A ping function that pings all clients currently connected and removes them if necessary

@app.route('/')
def hello():
    return "Hello World!"

if __name__ == '__main__':
    app.run()