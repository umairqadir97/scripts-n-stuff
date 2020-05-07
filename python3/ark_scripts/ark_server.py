# Commands for Ark server maintenance
# Lucas Rountree, 2020
#
# Import as module or run from shell.
#
#

# Import common modules
import sys
from subprocess import run

# Import custom modules
from ark_rcon import tcp

# Populate variables
Home = '/home/steam'
Path = Home + '/ShooterGame/Binaries/Linux/ShooterGameServer'
Map = 'TheIsland'
Session = 'ServerName'
Server_Pass = ''
Query_Port = 27015
Max_Players = 10
Rcon_Enabled = True
Rcon_Port = 32330
Rcon_Pass = ''
Host = 'localhost'
Options = ('-server', '-log')

# Set up rcon command
rcon = tcp(Host, Rcon_Port, Rcon_Pass).command

def start():
        Server_Path = Home + Path
        if Rcon_Enabled = True:
            Rcon_Command = '?RCONEnabled=True?RCONPort=' + Rcon_Port + '?ServerAdminPassword=' + Rcon_Pass
        else:
            Rcon_Command = '?RCONEnabled=False'
        Server_Command = Map + '?Listen?SessionName=' + Session + '?ServerPassword=' + Server_Pass + '?QueryPort=' + '?MaxPlayers=' + Max_Players + Rcon_Command
        Command_Options = ''
        for I,X in enumerate(Options):
            if I == len(Options) - 1:
                Command_Options += X
            else:
                Command_Options += X + ' '
        try:
            Start_Server = run([Server_path, Server_Command, Command_Options], capture_output=True)
        except:
            return sys.exc_info()
        else:
            if Start_Server.stderr:
                return Start_Server.stderr
        return Start_Server.stdout

def stop():
    try:
        Save_Request = rcon('SaveWorld')
    except:
        return sys.exc_info()
    else:
        if Save_Request[1] == 'World Saved'
            try:
                Stop_Request = rcon('DoExit')
            except:
                return sys.exc_info()
            else:
                return Stop_Request
        return Save_Request

def scrub():
    try:
        Scrub_Request = rcon('DestroyWildDinos')
    except:
        return sys.exc_info()
    else:
        return Scrub_Request

def update():
    try:
        Update_Server = run(['steamcmd', '+login', 'anonymous', '+force_install_dir', Home, '+app_update', '376030', '+quit'], capture_output=True)
    except:
        return sys.exc_info()
    else:
        if Update_Server.stderr:
            return Update_Server.stderr
    return Update_Server.stdout
