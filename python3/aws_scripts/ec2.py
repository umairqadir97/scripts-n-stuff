# Run actions against an ec2 instance
# Lucas Rountree 2021
import sys
import general_modules as mod

# MFA_Profile = input('MFA Profile Name: ')
# AWS_Region = input('AWS Region: ')

#ses = mod.set_session(MFA_Profile, AWS_Region)
#ec2 = mod.ec2(ses)
#ec2_info = mod.ec2_get_info(ses)

def list_instances():
    response = ec2_info.list_all_instances()
    if response[0]:
        for X in response[1]:
            ip_list = ec2.ip(X[1])
            if ip_list[0]:
                ips = ip_list[1][0]
            else:
                print(ip_list[1])
                sys.exit(1)
            print(X[0], '\n\tID:', X[1], '\n\tPrivate Ip:', ips[0], '\n\tPublic Ip:', ips[1])
    else:
        print(response[1])
        sys.exit(1)

def get_id(IN):
    response = ec2.id(IN)
    if not response[0]:
        response = ec2.id_from_ip(IN)
        if not response[0]:
            print(response[1])
            sys.exit(1)
    return response

def get_state():
    Instance_Identifier = input('Instance Name or IP: ')
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
    Instance_Identifier = input('Instance Name or IP: ')
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

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Get info from and run commands against AWS EC2 instances', prog='ec2')
    parser.add_argument('-p', action='store', type=str, default='default', help='AWS profile to use, from credentials file. Default is "default"')
    parser.add_argument('-r', action='store', type=str, default='us-west-2', help='AWS region, default is "us-west-2"')
    parser.add_argument('-c', action='store', type=str, choices=['list', 'state', 'start'], help='Function to run. list: list instances, state: get instance state, start: start instance')
#    parser.add_argument('-i', action='store', type=str, help='Instance name, id, or ip address')

    args = parser.parse_args()

    if args.p is False and args.r is False:
        parser.error('Profile (-p) and Region (-r) are REQUIRED')
    else:
        ses = mod.set_session(args.p, args.r)
        ec2 = mod.ec2(ses)
        ec2_info = mod.ec2_get_info(ses)
    if args.c == 'list':
        list_instances()
    elif args.c == 'state':
        print(get_state()[1])
    elif args.c == 'start':
        start()
    else:
        parser.error('Please use: list, state, or start')

else:
    MFA_Profile = input('MFA Profile Name: ')
    AWS_Region = input('AWS Region: ')
    ses = mod.set_session(MFA_Profile, AWS_Region)
    ec2 = mod.ec2(ses)
    ec2_info = mod.ec2_get_info(ses)
