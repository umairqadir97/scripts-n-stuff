# Python 3.9
# Grab MFA tokens and set up temporary session
# Lucas Rountree, Feb 2021
# Requires: python 3.9, boto3 (pip install boto3), custom log.py module

# Import Common Modules
import sys, boto3
from subprocess import run

# Import Custom Modules
#from log import LOG

#Log_File = '/var/log/aws_mfa.log'

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

# Set Up Commands
#log = LOG('MFA_LOGGER', Log_File, 'critical', 'info')

# Function to grab MFA device ARN and generate creds
def get_creds(TOKEN, USER, ACCOUNT):
    '''
    TOKEN: MFA device token
    USER: AWS account IAM user
    ACCOUNT: AWS account profile name in credentials file
    '''
    iam = set_session(ACCOUNT).client('iam')
    sts = set_session(ACCOUNT).client('sts')
    # Get MFA Device ARN
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

# Function to set Up Profile
def set_creds(User_Name, Device_Token, AWS_Account, MFA_Profile = 'aws-mfa', REGION = 'us-west-1', OUTPUT = 'table'):
    '''
    Sets temporary MFA credentials for AWS CLI
    import module: import aws-mfa
    run as module: aws-mfa.set_creds(User_Name, Device_Token, Account_Profile, MFA_Profile, Region, Output)
    run as script: python3 aws-mfa.py
    User_Name: IAM local user to get MFA token for
    Device_Token: Token key generated by physical device (your phone, usually)
    AWS_Account: AWS account name to get MFA access to, this is the credentials file profile name
    MFA_Profile: AWS credential file profile name to use for MFA credentials \
            (this is the profile name you will use in CLI commands, default is "aws-mfa")
    Region: Default region to set in config file, default is "us-west-1"
    Output: Default output type to set in config file, default is "table"
            Options:
                    json
                    table
                    text
    '''
    AWS_Creds = get_creds(Device_Token, User_Name, AWS_Account)
    if not AWS_Creds[0]:
        print(AWS_Creds[1])
        sys.exit(1)
    Key_ID, Secret_Key, Session_Token, Credential_Experation = AWS_Creds[1].values()
    try:
        run(['aws', 'configure', 'set', f'profile.{MFA_Profile}.aws_access_key_id', f'{Key_ID}'])
    except:
        print(sys.exc_info()[1])
    try:
        run(['aws', 'configure', 'set', f'profile.{MFA_Profile}.aws_secret_access_key', f'{Secret_Key}'])
    except:
        print(sys.exc_info()[1])
    try:
        run(['aws', 'configure', 'set', f'profile.{MFA_Profile}.aws_session_token', f'{Session_Token}'])
    except:
        print(sys.exc_info()[1])
    try:
        run(['aws', 'configure', 'set', f'profile.{MFA_Profile}.region', f'{REGION}'])
    except:
        print(sys.exc_info()[1])
    try:
        run(['aws', 'configure', 'set', f'profile.{MFA_Profile}.output', f'{OUTPUT}'])
    except:
        print(sys.exc_info()[1])

    # Close
    print(f'Session Token Written, Expires: {Credential_Experation}')

# Run as script
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Generate MFA credentials for AWS', prog='set_creds')
    parser.add_argument('-u', action='store', required=True, type=str, help='IAM username')
    parser.add_argument('-t', action='store', required=True, type=str, help='MFA device token')
    parser.add_argument('-a', action='store', required=True, type=str, help='AWS account name')
    parser.add_argument('-m', action='store', default='', help='Credential file profile name for mfa credentials, default: aws-mfa')
    parser.add_argument('-r', action='store', default='', help='Default AWS region, default: us-west-1')
    parser.add_argument('-o', action='store', default='', choices=['json', 'text', 'table'], help='AWS CLI output type, default: table')
    args = parser.parse_args()
    set_creds(args.u, args.t, args.a, args.m, args.r, args.o)
