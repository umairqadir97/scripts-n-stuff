import boto3, botocore
import sys

def set_session(PROFILE='default', REGION='us-west-2'):
    '''
    Provide AWS SDK session block
    aws_opsworks.set_session(PROFILE, REGION)
    PROFILE = AWS CLI profile to use (from credentials file), default is "default"
    REGION = AWS region to use, default is "us-west-2"
    '''
    try:
        session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    except:
        print(sys.exc_info()[1])
        sys.exit(1)
    return session

def get_user_access(STACK, SESSION):
    '''
    Output users with ssh/sudo access to the bastion servers in the opsworks stack
    aws_opsworks.get_user_access(STACK)
    STACK = stack id
    '''
    opsworks = SESSION.client('opsworks')
    try:
        user_list = [[X['IamUserArn'], X['Name']] for X in opsworks.describe_user_profiles()['UserProfiles']]
    except:
        print(sys.exc_info()[1])
        sys.exit(1)
    ssh_user_list = []
    sudo_user_list = []
    for USER in user_list:
        try:
            permissions_response = opsworks.describe_permissions(IamUserArn=USER[0], StackId=STACK[1])['Permissions']
        except:
            print(sys.exc_info()[1])
            sys.exit(1)
        for X in permissions_response:
            if X['AllowSsh']:
                ssh_user_list.append(USER[1])
            if X['AllowSudo']:
                sudo_user_list.append(USER[1])

    return({'stack_name': STACK[0], 'ssh': ssh_user_list, 'sudo': sudo_user_list})

def get_stacks(SESSION):
    '''
    Create a list of all stacks with two objects: 1- stack name, 2- stack id
    aws_opsworks.get_stacks(SESSION)
    SESSION = output of aws_opsworks.set_session(PROFILE, REGION)
    '''
    opsworks = SESSION.client('opsworks')
    stack_list = [[X['Name'], X['StackId']] for X in opsworks.describe_stacks()['Stacks']]
    return stack_list

def get_users(IN, SESSION):
    '''
    Get user permissions for stacks
    aws_opsworks.get_users(IN, SESSION)
    IN = [stack name, stack id] or "all" for all stacks
    SESSION = output of aws_opsworks.set_session(PROFILE, REGION)
    '''
    opsworks = session.client('opsworks')
    if IN == 'all':
        all_stacks = []
        for STACK in get_stacks(SESSION):
            all_stacks.append(get_user_access(STACK, SESSION))
        return all_stacks

    stack_data = []
    for STACK in get_stacks(SESSION):
        if STACK[0] == IN:
            stack_data = STACK
    if not stack_data:
        return False
    return get_user_access(stack_data, SESSION)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Get info from opsworks', prog='aws_opsworks')
    parser.add_argument('-p', action='store', default='default', type=str, help='AWS CLI profile, default: default')
    parser.add_argument('-r', action='store', default='us-west-2', type=str, help='AWS CLI region to run commands in, default: us-west-2')
    parser.add_argument('-s', action='store', default='all', type=str, help='Stack name, must be correct and is case sensative. Use "list" to print stack names. default: all (outputs users for all stacks)')

    args = parser.parse_args()
    session = set_session(args.p, args.r)
    if args.s == 'list':
        for X in get_stacks(session):
            print(X[0] + ":\n\t" + X[1])
    else:
        if args.s != 'all':
            response = get_users(args.s, session)
            if not response:
                print('Bad stack name!')
            else:
                print(response['stack_name'], '\n\tSSH:')
                for X in response['ssh']:
                    print('\t\t' + X)
                print('\n\tSUDO:')
                for X in response['sudo']:
                    print('\t\t' + X)
        else:
            for X in get_users(args.s, session):
                print(X['stack_name'], '\n\tSSH:')
                for I in X['ssh']:
                    print('\t\t' + I)
                print('\n\tSUDO:')
                for I in X['sudo']:
                    print('\t\t' + I)
