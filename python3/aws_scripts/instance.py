# Run actions against an ec2 instance
# Lucas Rountree 2021
import sys
sys.path.append('../custom_modules/aws_modules')
import general_modules as mod

MFA_Profile = input('MFA Profile Name: ')
AWS_Region = input('AWS Region: ')
Instance_Identifier = input('Instance Name or IP: ')

ses = mod.set_session(MFA_Profile, AWS_Region)
ec2 = mod.ec2(ses)

def get_id(IN):
    response = ec2.id(IN)[1]
    if not response:
        response = ec2.id_from_ip(IN)
    return response

def get_state():
    Instance_Id = get_id(Instance_Identifier)[1][0]
    try:
        get_state = ec2.state(Instance_Id)
    except:
        print('Can not find state for instance ID: ', Instance_Id)
        print(sys.exc_info()[1])
        sys.exit(1)
    if not get_state[0]:
        print(get_state[1])
        sys.exit(1)
    return get_state

def start():
    Instance_Id = get_id(Instance_Identifier)[1][0]
    ec2_client = ses.client('ec2')
    Instance_State = get_state()
    if Instance_State[1] == 'stopped':
        print('Starting instance: ', Instance_Id)
        try:
            response = ec2_client.start_instances(InstanceIds=[Instance_Id])
        except:
            print(sys.exc_info()[1])
            sys.exit(1)
        print('Start complete, state: ', response['StartingInstances'][0]['CurrentState']['Name'])
    else:
        print('Instance not in state: STOPPED')
        sys.exit(1)
