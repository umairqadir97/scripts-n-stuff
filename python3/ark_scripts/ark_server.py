# Commands for Ark server maintenance
# Lucas Rountree, 2020
#
# Import as module or run from shell.
# Requires rcon_server.yaml in same directory
#

# Import common modules
import os, sys, yaml
from subprocess import run
from datetime import datetime

# Import custom modules
from ark_rcon import tcp

# Populate variables
DateTime = datetime.now().strftime('%Y%m%d-%H%M%S') # Get current date and time
Backup_Name = 'Ark_Server-' + DateTime + '.tar.gz' # Backup file name
Backup_Destination = '/backup/ark_server/' # Directory path for backup file
Backup_Path = Backup_Destination + Backup_Name # Full backup path
Config_File = os.path.join(os.getcwd() + '/', 'rcon_server.yaml') # Path for config file rcon_server.yaml

for PATH in Backup_Destination, Backup_Path, Config_File: # Check that specified paths exist, error out if not
    if not os.path.exists(PATH):
        sys.exit('Path does not exist!: ' + PATH)

with open(Server_Config_File, 'r') as Input_File: # Pull key/values from yaml config file
    Config_Data = yaml.safe_load(Input_File)

for VAR in Config_Data: # Populate variables with yaml data
    globals()[str(VAR)] = Config_Data[VAR]

# Set up rcon command
rcon = tcp(Host, Rcon_Port, Rcon_Pass).command

# Define server command functions
def start():
        """Start the ark server
        Uses config info from rcon_server.yaml
        Usage: ark_server.start()
        Output: sys exit, stderr, or stdout
        """
        Server_Path = Steam_Home + Exec_Path
        if Rcon_Enabled == True:
            Rcon_Command = '?RCONEnabled=True?RCONPort=' + Rcon_Port + '?ServerAdminPassword=' + Rcon_Pass
        else:
            Rcon_Command = '?RCONEnabled=False'
        Server_Command = Map + '?Listen?SessionName=' + Session + '?ServerPassword=' + Server_Pass + '?QueryPort=' + '?MaxPlayers=' + Max_Players + Rcon_Command
#        Command_Options = ''
#        for I,X in enumerate(Options):
#            if I == len(Options) - 1:
#                Command_Options += X
#            else:
#                Command_Options += X + ' '
        try:
            Start_Server = run([Server_path, Server_Command, Command_Options], capture_output=True)
        except:
            return sys.exc_info()
        else:
            if Start_Server.stderr:
                return Start_Server.stderr
        return Start_Server.stdout

def stop():
    """Saves and then stops the ark server
    Usage: ark_server.stop()
    Output: sys exit or server response
    """
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
    """Destroys all wild dinos on the ark server
    Usage: ark_server.scrub()
    Output: sys exit or server response
    """
    try:
        Scrub_Request = rcon('DestroyWildDinos')
    except:
        return sys.exc_info()
    else:
        return Scrub_Request

def update():
    """Updates the ark server, which must be stopped first
    Usage: ark_server.update()
    Output: sys exit, stderr, or stdout
    """
    try:
        Update_Server = run(['steamcmd', '+login', 'anonymous', '+force_install_dir', Home, '+app_update', '376030', '+quit'], capture_output=True)
    except:
        return sys.exc_info()
    else:
        if Update_Server.stderr:
            return Update_Server.stderr
    return Update_Server.stdout

def backup():
    """Creates tar.gz of ark Saved directory at the specified (in rcon_server.yaml) backup location
    Usage: ark_server.backup()
    Output: sys exit, stderr, or stdout
    """
    try:
        Create_Backup = run(['tar', 'czf', Backup_Path, Home + '/ShooterGame/Saved'])
    except:
        return sys.exc_info()
    else:
        if Create_Backup.stderr:
            return Create_Backup.stderr
    return Create_Backup.stdout

def alert(Message):
    """Send a world broadcast message to the server, viewable by all players
    Usage: ark_server.alert(<message>)
    Output: sys exit or server response
    """
    try:
        Server_Response = rcon('Broadcast ' + Message)
    except:
        return sys.exc_info()
    return Server_Response

def send_command(Command):
    """This performs rcon(<command>), provided here for console commands not preconfigured by this script
    *** USE WITH CAUTION ***
    Usage: ark_server.command(<command>)
    Output: sys exit or server response
    """
    try:
        Server_Response = rcon(Command)
    except:
        return sys.exc_info()
    return Server_Response
