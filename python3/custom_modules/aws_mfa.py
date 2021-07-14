# Python 3.9
# Grab MFA tokens and set up temporary session
# Lucas Rountree, Feb 2021
# Requires: python 3.9, boto3 (pip3 install boto3)

# Import Common Modules
import sys, os, boto3, botocore, yaml
from subprocess import run

# Function to set up boto3 session
def set_session(ACCOUNT):
    '''
    ACCOUNT: AWS account profile name in credentials file
    '''
    try:
        session = boto3.Session(profile_name=ACCOUNT)
    except:
        print(sys.exc_info()[1])
        sys.exit(1)
    return session

# Function to grab MFA device ARN and generate creds
def get_creds(TOKEN, USER, ACCOUNT, ROLE = False, SESSION = False):
    '''
    TOKEN: MFA device token
    USER: AWS account IAM user
    ACCOUNT: AWS account profile name in credentials file
    ROLE: Role Name in IAM, specify to assume role
    '''
    iam = set_session(ACCOUNT).client('iam')
    sts = set_session(ACCOUNT).client('sts')
    # Get MFA Device ARN
    if TOKEN:
        try:
            Device_ARN = iam.list_mfa_devices(UserName=USER)['MFADevices'][0]['SerialNumber']
        except:
            return False, sys.exc_info()[1]
    # Get Credentials
        try:
            AWS_Creds = sts.get_session_token(SerialNumber=Device_ARN, TokenCode=TOKEN)['Credentials']
        except:
            return False, sys.exc_info()[1]
        return True, AWS_Creds
    if ROLE:
        # Assume Role
        try:
            AWS_Creds = sts.assume_role(RoleArn=ROLE, RoleSessionName=SESSION)['Credentials']
        except botocore.exceptions.ClientError as Error:
            if 'AccessDenied' in str(Error.args):
                return False, f'User does not have permission to assume role {ROLE}'
            else:
                return False, sys.exc_info()[1]
        except:
            return False, sys.exc_info()[1]
        return True, AWS_Creds

def assume_role(ROLE):
    if ROLE.split(':')[0] == 'arn':
        return ROLE
    elif os.path.isfile(ROLE.split(':')[0]):
        yaml_file = yaml.full_load(open(r'%s' %ROLE.split(':')[0]))
        acct_id = yaml_file[ROLE.split(':')[1]]
        return str('arn:aws:iam::' + acct_id + ':role/' + ROLE.split(':')[2])
    else:
        try:
            Role_ARN = iam.get_role(RoleName=ROLE)['Role']['Arn']
        except:
            return False, sys.exc_info()[1]
        return Role_ARN
    return False, 'Bad Role Input'

# Function to set Up Profile
def set_creds(User_Name = False, Device_Token = False, AWS_Account = False, MFA_Profile = 'aws-mfa', Assume_Role = False, REGION = 'us-west-1', OUTPUT = 'table'):
    '''
    Sets temporary MFA credentials for AWS CLI
    import module: import aws-mfa
    run as module: aws-mfa.set_creds(User_Name, Device_Token, Account_Profile, MFA_Profile, Region, Output)
    run as script: python3 aws-mfa.py
    User_Name: IAM local user to get MFA token for
    Device_Token: Token key generated by physical device (your phone, usually)
    AWS_Account: AWS account name to get MFA access to, this is the credentials file profile name
    Assume_Role: IAM Role name to assume
        FORMAT:
            [NAME] - assume role in current profile
            [ARN] - cross account role to assume
            [FILE:ACCOUNT:ROLE] - yaml file with account name and id
    MFA_Profile: AWS credential file profile name to use for MFA credentials 
            (this is the profile name you will use in CLI commands, default is "aws-mfa")
    Region: Default region to set in config file, default is "us-west-1"
    Output: Default output type to set in config file, default is "table"
            Options:
                    json
                    table
                    text
    '''
    if Assume_Role:
        Assume_Role = assume_role(Assume_Role)
        AWS_Creds = get_creds(Device_Token, User_Name, AWS_Account, Assume_Role, MFA_Profile)
    else:
        AWS_Creds = get_creds(Device_Token, User_Name, AWS_Account)
    if not AWS_Creds[0]:
        print(AWS_Creds[1])
        sys.exit(1)
    Key_ID, Secret_Key, Session_Token, Credential_Experation = AWS_Creds[1].values()
    try:
        run(['aws', 'configure', 'set', f'profile.{MFA_Profile}.aws_access_key_id', Key_ID])
    except:
        print(sys.exc_info()[1])
    try:
        run(['aws', 'configure', 'set', f'profile.{MFA_Profile}.aws_secret_access_key', Secret_Key])
    except:
        print(sys.exc_info()[1])
    try:
        run(['aws', 'configure', 'set', f'profile.{MFA_Profile}.aws_session_token', Session_Token])
    except:
        print(sys.exc_info()[1])
    try:
        run(['aws', 'configure', 'set', f'profile.{MFA_Profile}.region', REGION])
    except:
        print(sys.exc_info()[1])
    try:
        run(['aws', 'configure', 'set', f'profile.{MFA_Profile}.output', OUTPUT])
    except:
        print(sys.exc_info()[1])

    # Close
    print(f'Session Token Written, Expires: {Credential_Experation}')

# Run as script
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Generate MFA credentials for AWS', prog='aws-mfa')
    parser.add_argument('-u', action='store', default=False, type=str, help='IAM username')
    parser.add_argument('-a', action='store', default=False, type=str, help='AWS account name')
    parser.add_argument('-n', action='store', default='aws-mfa', type=str, help='Credential file profile name for mfa or cross account credentials')
    parser.add_argument('-x', action='store', default=False, type=str, help='IAM Role name to assume')
    parser.add_argument('-r', action='store', default='us-west-1', type=str, help='Default AWS region, default: us-west-1')
    parser.add_argument('-o', action='store', default='table', type=str, choices=['json', 'text', 'table'], help='AWS CLI output type')
    parser.add_argument('-t', action='store', default=False, type=str, help='MFA device token')
    args = parser.parse_args()
    if args.u and (args.a is False or args.n is False or args.t is False):
        parser.error('-u requires -a, -n, and -t')
    if args.a and args.u and (args.n is False or args.t is False):
        parser.error('-a with -u requires -n and -t')
    if args.x and (args.a is False or args.n is False):
        parser.error('-x requires -n')
    if args.t and (args.u is False or args.a is False or args.n is False):
        parser.error('-t requires -u, -a, and -n')
    if not args.u and not args.n:
        parser.error('You must supply valid options')
    set_creds(args.u, args.t, args.a, args.n, args.x, args.r, args.o)
