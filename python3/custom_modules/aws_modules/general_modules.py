# general and frequently used AWS related modules

import boto3, botocore.exceptions, sys

def set_session(PROFILE, REGION='us-west-2'):
    try:
        session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    except:
        print(sys.exc_info()[1])
        sys.exit(1)
    return session

class ec2:
    '''
    ec2 modules
    set session first, call ec2 with session:
    session = general_modules.set_session(PROFILE, REGION)
    ec2 = general_modules.ec2(session)
    '''

    def __init__(self, session):
        self.ec2_client = session.client('ec2')

    def name_by_id(self, NAME):
        '''
        Return instance ID by using Name tag
        NAME = value of Name tag
        '''
        try:
            response = self.ec2_client.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [NAME]}])['Reservations'][0]['Instances'][0]['InstanceId']
        except:
            return False, str(sys.exc_info())
        return True, response


# Run as a sript
#if __name__ == '__main__':
#    from argparse import ArgumentParser as arg

#    parser = arg(description='Useful AWS python modules', prog='mod')
#    parser.add_argument('-p', required=True, action='store', type=str, help='AWS profile to use *required*')
#    parser.add_argument('-r', required=True, action='store', type=str, help='AWS region to use *required*')
#    parser.add_argument('-s', required=True, action='store', choices=['ec2'], help='AWS service module')
    
