# Functional rcon for Ark
# Lucas Rountree, 2020
#
# Import as module or run from shell.
#
# Usage:
# 
## Request Types:
# 3: SERVERDATA_AUTH
# 2: SERVERDATA_EXECCOMMAND
## Response Types:
# 2: SERVERDATA_AUTH_RESPONSE
# 0: SERVERDATA_RESPONSE_VALUE

# Import Common Modules
import sys
import socket
import logging
from struct import pack, unpack, calcsize

# Populate variables
Buffer = 4096
packet = self.socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set up log function
def log(ERROR, EXIT_CODE):
    print(ERROR)
    sys.exit(EXIT_CODE)

# Set up socket operations as a class
class tcp(self):
    """help file here
    """

    def create_message(ID,BODY,TYPE):
        Size = len(BODY) + 10 # get packet size
        Message = BODY.encode('utf-8') # encode message body
        return pack('<3i{0}s'.format(len(BODY)), Size, ID, Message) + b'\x00\x00' # format the packet for the rcon server

    def get_response():
        Iteration = 0
        while Iteration < 11:
            Response = packet.recv(calcsize('<3i'))
            if len(Response) != 0:
                break
            Iteration += 1
        if Response:
            (SIZE, ID, TYPE) = unpack('<3i', Response)
            BODY = packet.recv(SIZE - 8)
            return SIZE, ID, TYPE, BODY
        else:
            return 'NONE'

# Set up rcon function
def rcon(Host = 'localhost', Port = '32330', Command, Pass):
    try:
        packet.connect((Host,Port)) # Connect to rcon host
    except:
        #exception here
        log('print error here')
    Connection_Response = tcp.get_response()
    if Connection_Response != X: # Check repsonse to connection request
        log('print error here', 0)
    try:
        packet.send(tcp.create_message(3,Pass,3)) # Authenticate with rcon host
    except:
        #exception here
        log('print error here')
    Auth_Response = tcp.get_response()
    if Auth_Response != X: # Check authentication response
        log('print error here', 0)
    try:
        packet.send(tcp.create_message(2,Command,2)) # Send command request to rcon host
    except:
        #exception here
        log('print error here')
    Send_Response = tcp.get_response()
    if Send_Response != X: # Check command response
        log('print error here', 0)
    packet.close() # Close connection
    
    return Send_Response

# Run as script
if __name__ == '__main__':
    try: # Confirm if all options were passed
        Host, Port, Command, Pass = sys.argv[1:] # Populate variables with options
    except:
        if not sys.argv[1]: # Confirm if any options were passed
            log('print error here', 0)
        elif sys.argv[:2] and not sys.argv[3:]: # Check if only command and password were sent
            Command, Pass = sys.argv[1:]
            rcon(Command = Command, Pass = Pass)
            log('print error here', 1)
    rcon(Host, Port, Command, Pass)
