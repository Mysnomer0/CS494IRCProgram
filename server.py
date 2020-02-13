# Milan Mauck

from flask import *


# Create the server as an HTTP app
app = Flask('CS494IRCServer')

# The list of rooms
listOfRooms = []

# The list rooms command
@app.route('/rooms', methods=['POST'])
def ListRooms():
    if request.method == 'POST':
        listOfRoomsAsString = ''
        for i in range(len(listOfRooms)):
            listOfRoomsAsString += listOfRooms[i].name
        return listOfRoomsAsString

@app.route('/')
def hello():
    return "Hello World!"

if __name__ == '__main__':
    app.run()