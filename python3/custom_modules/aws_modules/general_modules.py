# general and frequently used AWS related modules

import boto3, botocore.exceptions, sys

import boto3, botocore

def set_session(PROFILE='default', REGION='us-west-2'):
    '''
    Provide AWS SDK session block
    set_session(PROFILE, REGION)
    PROFILE = AWS CLI profile to use (from credentials file), default is "default"
    REGION = AWS region to use, default is "us-west-2"
    '''
    try:
        session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    except botocore.exceptions.ProfileNotFound as ERROR:
        print(ERROR)
        sys.exit(1)
    except TypeError as ERROR:
        print(ERROR)
        sys.exit(1)
    except:
        print(sys.exc_info()[1])
        sys.exit(1)
    return session

class ec2_get_info:
    '''
    ec2 modules
    set session first, call ec2 with session:
    session = general_modules.set_session(PROFILE, REGION)
    ec2 = general_modules.ec2(session)
    '''

    def __init__(self, session):
        self.ec2_client = session.client('ec2')

    def get_regions(self):
        '''
        Return a list of all regions
        '''
        try:
            response = [X['RegionName'] for X in self.ec2_client.describe_regions()['Regions']]
        except:
            return False, str(sys.exc_info()[1])
        return True, response

    def list_all_instances(self):
        '''
        Return a list of dictonary items containing name:id of all instances
        '''
        try:
            grab_data = self.ec2_client.describe_instances()['Reservations']
        except:
            return False, str(sys.exc_info()[1])
        response = []
        for ITEM in grab_data:
            for INSTANCE in ITEM['Instances']:
                name_id = False
                for NAME in INSTANCE['Tags']:
                    if NAME['Key'] == 'Name':
                        name_id = [NAME['Value'], INSTANCE['InstanceId']]
                if not name_id:
                    response.append(['', INSTANCE['InstanceId']])
                else:
                    response.append(name_id)
        return True, response

    def instance_info_by_name(self, NAME):
        '''
        Return instance json by using Name tag
        NAME = value of Name tag
        TIP: use wildcard on either end to match part of the Name tag
        '''
        try:
            response = self.ec2_client.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [NAME]}])['Reservations']
        except:
            return False, str(sys.exc_info()[1])
        return True, response

    def instance_info_by_id(self, ID):
        '''
        Return instance json by instance ID
        ID = Instance ID
        '''
        try:
            response = self.ec2_client.describe_instances(Filters=[{'Name': 'instance-id', 'Values': [ID]}])['Reservations']
        except:
            return False, str(sys.exc_info()[1])
        return True, response

    def instance_info_by_ip(self, IP):
        '''
        Return instance json by private or public IP
        IP = private IP address
        '''
        try:
            response = self.ec2_client.describe_instances(Filters=[{'Name': 'private-ip-address', 'Values': [IP]}])['Reservations']
        except:
            return False, str(sys.exc_info()[1])
        if not response:
            try:
                response = self.ec2_client.describe_instances(Filters=[{'Name': 'network-interface.association.public-ip', 'Values': [IP]}])['Reservations']
            except:
                return False, str(sys.exc_info()[1])
        return True, response

class iam_get_info:
    '''
    iam modules
    set session first, call iam with session:
    session = general_modules.set_session(PROFILE, REGION)
    iam = general_modules.iam(session)
    '''

    def __init__(self, session):
        self.iam_client = session.client('iam')

    def find_roles(self, NAME = 'ALL'):
        '''
        Return a list of IAM roles that match pattern NAME
        NAME = Role name pattern to match, ALL to list all roles
        '''
        try:
            list_roles = self.iam_client.list_roles()
        except:
            return False, str(sys.exc_info()[1])
        Role_List = []
        for ROLE in list_roles['Roles']:
            Role_List.append(ROLE['RoleName'])
        while 'Marker' in list_roles:
            list_roles = self.iam_client.list_roles(Marker=list_roles['Marker'])
            for ROLE in list_roles['Roles']:
                Role_List.append(ROLE['RoleName'])
        if NAME == 'ALL':
            return True, Role_List 
        Found_Roles = []
        for ROLE in Role_List:
            if NAME in ROLE:
                Found_Roles.append(ROLE)
        return True, Found_Roles

    def role_info_by_name(self, NAME):
        '''
        Return IAM resource info by Name
        NAME = Role name
        '''
        try:
            response = self.iam_client.get_role(RoleName=NAME)
        except:
            return False, str(sys.exc_info()[1])
        return True, response

class s3_get_info:
    '''
    s3 modules to pull info from resources
    set session first, call iam with session:
    session = general_modules.set_session(PROFILE, REGION)
    s3 = general_modules.s3(session)
    '''

    def __init__(self, session):
        self.s3_client = session.client('s3')

    def find_buckets(self, NAME = 'ALL'):
        '''
        Return a list of buckets that match pattern NAME
        NAME = bucket name pattern to match, ALL to list all roles
        '''
        try:
            Bucket_List = [X['Name'] for X in self.s3_client.list_buckets()['Buckets']]
        except:
            return False, str(sys.exc_info()[1])
        if NAME == 'ALL':
            return True, Bucket_List
        else:
            response = []
            for X in Bucket_List:
                if NAME in X:
                    response.append(X)
        if not response:
            return False, response
        return True, response

    def prefix_list(self, BUCKET, PREFIX = False):
        '''
        Return a list of prefixes for a given bucket
        BUCKET = S3 bucket name
        PREFIX = Prefix to look in
        '''
        if PREFIX:
            try:
                Object_List = self.s3_client.list_objects(Bucket=BUCKET, Prefix=PREFIX)['Contents']
            except:
                return False, str(sys.exc_info()[1])
        else:
            try:
                Object_List = self.s3_client.list_objects(Bucket=BUCKET)['Contents']
            except:
                return False, str(sys.exc_info()[1])
        Prefix_List = []
        for X in Object_List:
            Object_Line = X['Key']
            Object_Line = Object_Line.split(PREFIX + '/')[1]
            prefix = Object_Line.split('/')[0]
            if X['Key'].split(prefix)[1]:
                if prefix not in Prefix_List:
                    Prefix_List.append(prefix)
        return True, Prefix_List

class ec2(ec2_get_info):
    
    def __init__(self, session):
        ec2_get_info.__init__(self, session)
        self.session = session
        
    def name(self, NAME):
        '''
        Find instance name
        NAME = pattern to match, use wildcards to pattern match
        '''
        instance_info = ec2_get_info(self.session).instance_info_by_name(NAME)
        if not instance_info[0]:
            return False, instance_info[1]
        response = []
        for ITEM in instance_info[1]:
            for INSTANCE in ITEM['Instances']:
                for TAG in INSTANCE['Tags']:
                    if TAG['Key'] == 'Name':
                        response.append(TAG['Value'])
        return True, response

    def id(self, NAME):
        '''
        Return instance ID by name tag
        NAME = instance name tag value
        can use wildcards
        '''
        instance_info = ec2_get_info(self.session).instance_info_by_name(NAME)
        if not instance_info[0] or not instance_info[1]:
            return False, instance_info[1]
        response = []
        for ITEM in instance_info[1]:
            for INSTANCE in ITEM['Instances']:
                response.append(INSTANCE['InstanceId'])
        return True, response

    def ip(self, ID):
        '''
        Return IP addresses of instance by ID
        ID = Instance ID
        '''
        instance_info = ec2_get_info(self.session).instance_info_by_id(ID)
        if not instance_info[0]:
            return False, instance_info[1]
        response = []
        for ITEM in instance_info[1]:
            for INSTANCE in ITEM['Instances']:
                if 'PrivateIpAddress' in INSTANCE:
                    ip = [INSTANCE['PrivateIpAddress']]
                else:
                    ip = ['NONE']
                if 'PublicIpAddress' in INSTANCE:
                    ip.append(INSTANCE['PublicIpAddress'])
                else:
                    ip.append('NONE')
                response.append(ip)
        return True, response

    def id_from_ip(self, IP):
        '''
        Return instance ID and Tag:Name from private or public IP address
        IP = private/public IP address
        '''
        instance_info = ec2_get_info(self.session).instance_info_by_ip(IP)
        if not instance_info[0]:
            return False, instance_info[1]
        response = []
        for ITEM in instance_info[1]:
            for INSTANCE in ITEM['Instances']:
                response.append(INSTANCE['InstanceId'])
                for TAG in INSTANCE['Tags']:
                    if TAG['Key'] == 'Name':                                                                response.append(TAG['Value'])
        return True, response

    def key_pair(self, ID):
        '''
        Return key pair name by instance ID
        ID = Instance ID
        '''
        instance_info = ec2_get_info(self.session).instance_info_by_id(ID)
        if not instance_info[0]:
            return False, instance_info[1]
        if 'KeyName' in instance_info[1][0]['Instances'][0]:
            return True, instance_info[1][0]['Instances'][0]['KeyName']
        else:
             return True, ''

    def security_groups(self, ID):
        '''
        Return list of security groups by instance ID
        ID = Instance ID
        '''
        instance_info = ec2_get_info(self.session).instance_info_by_id(ID)
        if not instance_info[0]:
            return instance_info[1]
        return True, instance_info[1][0]['Instances'][0]['SecurityGroups']

    def state(self, ID):
        '''
        Return state by instance ID
        ID = Instance ID
        '''
        instance_info = ec2_get_info(self.session).instance_info_by_id(ID)
        if not instance_info[0]:
            return False, instance_info[1]
        return True, instance_info[1][0]['Instances'][0]['State']['Name']

class iam(iam_get_info):

    def __init__(self, session):
        iam_get_info.__init__(self, session)
        self.session = session

    def list_roles(self, NAME = 'ALL'):
       '''
       Return a list of role names, can pattern match
       NAME = Pattern to match, or ALL to list all roles (default)
       '''
       try:
           response = iam_get_info(self.session).find_roles(NAME)
       except:
           return False, str(sys.exc_info()[1])
       if not response[0]:
           return False, response[1]
       return True, response[1]

    def role_arn(self, NAME):
       try:
           response = iam_get_info(self.session).role_info_by_name(NAME)
       except:
           return False, str(sys.exc_info()[1])
       if not response[0]:
           return False, response[1]

       return True, response[1]['Role']['Arn']

class s3(s3_get_info):

    def __init__(self, session):
        s3_get_info.__init__(self, session)
        self.session = session
        self.s3_client = self.session.client('s3')

    def change_lf(self, NAME):
#        try:
#            lf_config = open(FILE, 'r')
#        except:
#            return False, str(sys.exc_info()[1])
        try:
 #           response = self.s3_client.put_bucket_lifecycle_configuration(Bucket=NAME, LifecycleConfiguration=lf_config.read().rstrip('\n'))
            response = self.s3_client.put_bucket_lifecycle_configuration(Bucket=NAME, LifecycleConfiguration={'Rules': [{'ID': 'theta_14d_lifecycle_policy','Prefix': '','Status': 'Enabled','Expiration': {'Days': 14},}]})
        except:
            return False, str(sys.exc_info()[1])
#        lf_config.close()
        return True, response
        
# Run as a sript
#if __name__ == '__main__':
#    from argparse import ArgumentParser as arg

#    parser = arg(description='Useful AWS python modules', prog='mod')
#    parser.add_argument('-p', required=True, action='store', type=str, help='AWS profile to use *required*')
#    parser.add_argument('-r', required=True, action='store', type=str, help='AWS region to use *required*')
#    parser.add_argument('-s', required=True, action='store', choices=['ec2'], help='AWS service module')
    
