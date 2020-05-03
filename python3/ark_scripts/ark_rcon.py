# Functional rcon for Ark
# Lucas Rountree, 2020
#
# Import as module or run from shell.
#
# Usage:
# import ark_rcon
# connect = ark_rcon.tcp(Host, Port, Pass)
# rcon = connect.command
# (or: rcon = ark_rcon.tcp(Host, Port, Pass).command)
# (or: from ark_rcon import tcp, rcon = tcp(Host, Port, Pass).command)
# rcon(<command>)
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
from struct import pack, unpack, calcsize
#from datetime import datetime
#from log import LOG as log

# Populate variables
Buffer = 4096
packet = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Log_File = '/home/steam/3lemontrees/ShooterGame/Saved/Logs/rcon-' + datetime.datetime.now().strftime('%Y.%m.%d-%H.%M.%S' + '.log'

# Set up log/exit function
#log = log('rcon_logger', Log_File, 'critical', 'debug')

# Set up socket operations as a class
class tcp():
    """help file here
    """
    def __init__(self, Host = 'localhost', Port = 32330, Pass = False):
        self.Host = Host
        self.Port = Port
        self.Pass = Pass
    
    def get_response():
        Iteration = 0
        while Iteration < 11:
            Respose = packet.recv(calcsize('<3i'))
            if len(Response) != 0:
                break
            Iteration += 1
            if Response:
                (SIZE, ID, TYPE) = unpack('<3i', Response)
                BODY = packet.recv (SIZE - 8)
                return SIZE, ID, TYPE, BODY
            else:
                return False
    
    def create_message(ID,BODY,TYPE):
        Size = len(BODY) + 10 # get packet size
        Message = BODY.encode('utf-8') # encode message body
        return pack('<3i{0}s'.format(len(BODY)), Size, ID, Message) + b'\x00\x00' # format the packet for the rcon server

    def auth(self):
        try:
            Connection_Response = packet.connect((self.Host,self.Port)) # Connect to rcon host
        except:
            packet.close()
            return str(sys.exc_info()[1])
        else:
            if Connection_Response[3].decode('utf-8') != 'Keep Alive': # Check response to connection request
                return Connection_Response[3].decode('utf-8')
            if Pass:
                try:
                    packet.send(self.tcp.create_message(3,self.Pass,3)) # Authenticate with rcon host
                except:
                    packet.close()
                    return str(sys.exc_info()[1])
                else:
                    Auth_Response = self.tcp.get_response()
                if Auth_Response[1] != 3: # Check authentication response
                    packet.close()
                    return Auth_Response[3].decode('utf-8')
        return True

    def command(self, Command):
        Auth = self.tcp.auth()
        if Auth != True:
            packet_close()
            return Auth
        try:
            packet.send(self.tcp.create_message(2,Command,2)) # Send command request to rcon host
        except:
            packet_close()
            return str(sys.exc_info()[1])
        else:
            Send_Response = self.tcp.get_response()
        if Send_Response[1] != 2 or Send_Response[2] != 0:
            packet_close()
            return 'Unknown error- response ID or Type does not match command request! ID: {0}, Type: {1}'.format(Send_Response[1], Send_Response[2])
        packet.close() # Close connection
        return Send_Response[3].decode('utf-8') # Send server response, will contain response data or error data for processing later

# Run as script
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Connect, authenticate with, and send commands to the Ark rcon host server.', prog='ark_rcon')
    parser.add_argument('-H', action='store', default='localhost', help='Hostname or IP address of the rcon host. Default: localhost')
    parser.add_argument('-P', action='store', default='32330', help='Port used by the host for rcon communication. Default: 32330')
    parser.add_argument('-p', action='store', default=False, help='Password to authenticate with the rcon host. Default: None')
    parser.add_argument('-c', action='store', required=True, help='Command to send to the rcon host. *Required*')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0', help='Get current version of ark_rcon.py')
    args = parser.parse_args()

    rcon = tcp(args.H, args.P, args.p)
    Response = rcon.command(args.c)
    print(Response)
