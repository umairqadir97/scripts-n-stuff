# Python 3.9
# Custom modules for docker things
# Requires: Dockerfile, docker, python3

# Import common modules
import sys, docker

# Set up variables

# Set up Modules
client = docker.from_env()

# Check for image
def check_image(IMAGE):
    '''
    custom_docker_modules.check_image(<IMAGE>)
    IMAGE: image name and tag, like ubuntu:latest
    '''
    try:
        Check_Result = client.images.list(IMAGE)
    except:
        return False, f'Failed to check for image {IMAGE}: ' + str(sys.exc_info()[1])
    if not Check_Result:
        return False, f'Image {IMAGE} not found in local cache'
    return True, f'Image {IMAGE} already in local cache'

# Create image
def build_image(FILE, TAG, PATH):
    '''
    custom_docker_modules.build_image(<FILE>, <TAG>, <PATH>)
    FILE: name of relevant dockerfile
    TAG: image name and tag, like ubuntu:latest
    PATH: context path, where relevant files are located
    '''
    try:
        client.images.build(dockerfile = FILE, tag = TAG, path = PATH)
    except:
        return False, f'Failed to build image {TAG}: ' + str(sys.exc_info()[1])
    return True, f'Built image {TAG}'

# Check for and create network
def create_net(NAME, DRIVER, IPV6, SCOPE):
    '''
    custom_docker_modules.network.create(<NAME>, <DRIVER>, <IPV6>, <SCOPE>)
    NAME: name of docker network
    DRIVER: bridge, host, overlay, macvlan, none
    IPV6: enable ipv6- True, False
    SCOPE: local, global, swarm
    '''
    try:
        Check_Net = client.networks.get(NAME)
    except docker.errors.NotFound:
        Check_Net = 'Create'
    except:
        return False, f'Failed to check for network {NAME}: ' + str(sys.exc_info()[1])
    else:
        return True, f'Network {NAME} exists, skipping create'
    if Check_Net == 'Create':
        try:
            Create_Net = client.networks.create(NAME, driver=DRIVER, ipv6=IPV6, scope=SCOPE)
        except:
            return False, f'Failed to create network {NAME}: ' + str(sys.exc_info()[1])
    if Create_Net[0] == 0:
        return True, 'Created network {Name}'
    else:
        return False, f'Failed to create network {Name}: ' + Create_Net[1]

# Run container
def run_container(HOSTNAME, IMAGE, *VOLS):
    '''
    custom_docker_modules.run_container(<HOSTNAME>, <IMAGE>, <VOLS>)
    HOSTNAME: FQDN of container
    IMAGE: image name and tag to build container from
    VOLS: optional list of volumes to mount/bind to container, use standard docker format- 
          '/source/path:/dest/path:opts', seperated by commas
    '''
    NAME = HOSTNAME.split('.')[0]
    if not VOLS or VOLS[0] is None:
        try:
            client.containers.run(IMAGE, detach=True, stdin_open=True, tty=True, name=NAME, hostname=HOSTNAME)
        except:
            return False, f'Failed to run {NAME}: ' + str(sys.exc_info()[1])
    else:
        Vol_Dict={}
        for VOLUME in VOLS:
            VOLUME = VOLUME.split(':')
            if len(VOLUME) > 3:
                return False, 'Too many values in container run volume option: ' + str(':'.join({VOLUME}))
            elif len(VOLUME) == 3:
                Vol_Dict[VOLUME[0]] = {'bind': VOLUME[1], 'mode': VOLUME[2]}
            else:
                Vol_Dict[VOLUME[0]] = {'bind': VOLUME[1]}
        try:
            client.containers.run(IMAGE, detach=True, stdin_open=True, tty=True, volumes=Vol_Dict, name=NAME, hostname=HOSTNAME)
        except:
            return False, f'Failed to run {NAME}: ' + str(sys.exc_info()[1])
    if not client.containers.list(filters={'name': NAME}):
        return False, f'Container {NAME} was NOT created!'
    return True, f'Container {NAME} has been created'

# Check container status
def get_status(NAME):
    try:
        Target_Container = client.containers.get(NAME)
    except:
        return False, f'Failed to get target container: ' + str(sys.exc_info()[1])
    try:
        Container_Status = Target_Container.status
    except:
        return False, f'Failed to get container status: ' + str(sys.exc_info()[1])
    return True, Container_Status

# Execute Command on container
def send_command(NAME, COMMAND):
    '''
    custom_docker_modules.send_command(<NAME>, <COMMAND>)
    NAME: name of docker container
    COMMAND: the command to be run on the docker container
    OUTPUT: success or failure, as well as command output
    '''
    try:
        Target_Container = client.containers.get(NAME)
    except:
        return False, f'Failed to get target container: ' + str(sys.exc_info()[1])
    try:
        Command_Output = Target_Container.exec_run(COMMAND)
    except:
        return False, f'Failed to run command on {NAME}: ' + str(sys.exc_info()[1])
    if Command_Output[0] != 0:
        return False, Command_Output
    return True, Command_Output
