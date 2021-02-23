# python 3.9
# This script is intended to build an IPA server in a docker container
# Requires: custome_docker_modules.py, log.py, ipa.Dockerfile, parameters.yaml

# Import Common Modules
import sys, yaml
from subprocess import run

# Import Custom Modules
from log import LOG
import custom_docker_modules as CDM

# Set Up Generic Variables
#Host_IP = run(['hostname', '-i']).stdout
Context_Path = '.'
Parameter_File = 'parameters.yaml'
Log_File = 'ipa.log'

# Grab Parameter File Data
parameters = yaml.full_load(open(r'%s' %Parameter_File))

# Populate Custom Variables
Image_Version = parameters['Container_Image']
Docker_File = parameters['Docker_File']
Domain_Name = parameters['Domain_Name']
Host_FQDN = parameters['Node_FQDN']
Host_Shortname = Host_FQDN.split('.')[0]
Volumes = parameters['Volumes']
Zone_Rev_IP = parameters['Zone_Rev_IP']
Zone_Fwd_DNS = parameters['Zone_Fwd_DNS']
Realm_KRB = Zone_Fwd_DNS.upper()
IPA_Master_FQDN = parameters['Master_Nodes']['MASTER_1'][0] + '.' + Zone_Fwd_DNS

# Create Hosts Block
Hosts_Block = f'\\n# IPA Cluster Block'
for NODE in parameters['Master_Nodes'], parameters['Satellite_Nodes']:
    for KEY in NODE.keys():
        if NODE[KEY][0] != Host_Shortname:
            Hosts_Block += f'\\n{NODE[KEY][1]}\\t{NODE[KEY][0]}.{Domain_Name} {NODE[KEY][0]}'

# Set Up Modules
log = LOG('IPA_Logger', Log_File, 'critical', 'info')

# Check For IPA Image, build if not found
check_image = CDM.check_image(Image_Version)
if check_image[0]:
    log.info(check_image[1])
elif check_image[1].split() == 'Failed':
    log.critical(check_image[1])
    sys.exit(1)
else:
    log.info(check_image[1])
    log.info('Building new image from dockerfile...')
    build_result = CDM.build_image(Docker_File, Image_Version, Context_Path)
    if build_result[0]:
        log.info(build_result[1])
    else:
        log.critical(build_result[1])
        sys.exit(1)

# Run IPA Container
run_result = CDM.run_container(Host_FQDN, Image_Version, Volumes)
if run_result[0]:
    log.info(run_result[1])
else:
    log.critical(run_result[1])
    sys.exit(1)

# Configure IPA
container_status = CDM.get_status(Host_Shortname)
if not container_status[0]:
    log.critical(container_status)
    sys.exit(1)
elif container_status[1] != 'running':
    log.critical(f'Container status: {container_status}')
    sys.exit(1)
else:
    log.info(f'Container is running')
##-update hosts file
command_result = CDM.send_command(Host_Shortname, f'bash -c \'echo -e "{Hosts_Block}" >> /etc/hosts\'')
if command_result[0]:
    log.info(f'Hosts file successfully written')
else:
    log.warning(f'Could not write to hosts file: ' + command_result[1][2])
##-generate and encrypt passwords, save encrypted passwords to local file
Admin_Password_Command = f'bash -c \'openssl rand -base64 24 >> /root/ipa/admin.pw\''
command_result = CDM.send_command(Host_Shortname, Admin_Password_Command)
if command_result[0]:
    log.info(f'Admin password generated and written to password file')
else:
    log.warning(f'Could not generate admin password or write to password file')
DM_Password_Command = f'bash -c \'openssl rand -base64 24 >> /root/ipa/directorymanager.pw\''
command_result = CDM.send_command(Host_Shortname, DM_Password_Command)
if command_result[0]:
    log.info(f'Directory Manager password generated and written to password file')
else:
    log.warning(f'Could not generate directory manager password or write to password file')
##-install IPA
Install_Command = '\'bash -c '
if Host_Shortname == parameters['Master_Nodes']['MASTER_1'][0]:
    Install_Command += parameters['Master1_Command'] + ' '
    for OPT in parameters['Master1_Options']:
        if OPT.split('=')[0] == 'reverse-zone':
            Install_Command += '--' + OPT.replace('VAL', Zone_Rev_IP) + ' '
        elif OPT.split('=')[0] == 'realm':
            Install_Command += '--' + OPT.replace('VAL', Realm_KRB) + ' '
        elif OPT.split('=')[0] == 'hostname':
            Install_Command += '--' + OPT.replace('VAL', IPA_Master_FQDN) + ' '
        elif OPT.split('=')[0] == 'ds-password':
            Install_Command += '--' + OPT.replace('VAL', '$(< /root/ipa/directorymanager.pw)') + ' '
        else:
            Install_Command += '--' + OPT + ' '
elif Host_Shortname == parameters['Master_Nodes']['MASTER_2'][0]:
    Install_Command += parameters['Replica_Command']
    for OPT in parameters['Master2_Options']:
        Install_Command += '--' + OPT + ' '
    for OPT in parameters['Replica_Options']:
        if OPT.split('=')[0] == 'server':
            Install_Command += '--' + OPT.replace('VAL', IPA_Master_FQDN) + ' '
        elif OPT.split('=')[0] == 'principal':
            Install_Command += '--' + OPT.replace('VAL', 'admin') + ' '
        else:
            Install_Command += '--' + OPT + ' '
elif Host_Shortname == parameters['Satellite_Nodes']['SAT_1'][0] or Host_Shortname == parameters['Satellite_Nodes']['SAT_2'][0]:
    Install_Command += parameters['Replica_Command']
    for OPT in parameters['Replica_Options']:
        if OPT.split('=')[0] == 'server':
            Install_Command += '--' + OPT.replace('VAL', IPA_Master_FQDN) + ' '
        elif OPT.split('=')[0] == 'principal':
            Install_Command += '--' + OPT.replace('VAL', 'admin')
        else:
            Install_Command += '--' + OPT + ' '
for OPT in parameters['IPA_Install_Options']:
    if OPT.split('=')[0] == 'domain':
        Install_Command += '--' + OPT.replace('VAL', Zone_Fwd_DNS) + ' '
    elif OPT.split('=')[0] == 'admin-password':
        Install_Command += '--' + OPT.replace('VAL', '$(< /root/ipa/admin.pw)')
    else:
        Install_Command += '--' + OPT + ' '
Install_Command += '\''
command_result = CDM.send_command(Host_Shortname, Install_Command)
log.info(f'TEST COMMAND: ' + Install_Command)
if command_result[0]:
    log.info('IPA has been successfully installed')
else:
    log.warning(f'IPA failed to install: ' + command_result[1][1].decode('utf-8'))
##-master-01 config
###-install ipa master
###-add replicas
###-remove ipa pw files
###-remove p12 pw files
##-master-02 config
###-install ipa master replica
###-remove ipa pw files
###-remove p12 pw files


# Check and Exit Code
