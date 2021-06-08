# Module to perform tag work on specified resource
# Each resource has it's own function
# Supported Resources: EC2, AutoScalling Groups, RDS, ELBv2

# Import modules
import boto3, botocore.exceptions, sys

# Set up class to create tags
class create_tag:

    def __init__(self, PROFILE, REGION, KEY, VALUE):
        self.Tag_Key = KEY
        self.Tag_Value = VALUE
        try
            self.session = boto3.Session(profile_name=PROFILE, region_name=REGION)
        except:
            print(sys.exc_info()[1])
            sys.exit(1)

    # Add tag to EC2 resource
    def ec2(self, ID):
        ec2_client = session.client('ec2')
        try:
            ec2_client.create_tags(Resources=[ID], Tags=[{'Key': Tag_Key, 'Value': Tag_Value}])
        except:
            return False, str(sys.exc_info())
        return True

   # Add tag to AutoScaling Group
    def asg(self, ID):
        asg_client = session.client('autoscaling')
        try:
            asg_client.create_or_update_tags(Tags=[{'ResourceId': ID, 'Key': Tag_Key, 'Value': Tag_Value}])
        except:
            return False, str(sys.exc_info())
        return True

   # Add tag to RDS resource
   def rds(self, ID):
        rds_client = session.client('rds')
        try:
            rds_client.add_tags_to_resource(ResourceName=ID, Tags=[{'Key': Tag_Key, 'Value': Tag_Value}])
        except:
            return False, str(sys.exc_info())
        return True

    # Add tag to ELBv2 resource
    def elb(self, ID):
        '''
        ID = load balancer ARN
        '''
        elb_client = session.client('elbv2')
        try:
            elb_client.add_tags(ResourceArns=ID, Tags=[{'Key': Tag_Key, 'Value': Tag_Value}])
        except:
            return False, str(sys.exc_info())
        return True

    # Add tag to DocumentDB resource
    def ddb(self, ID):
        ddb_client = session.client('docdb')
        try:
            ddb_client.add_tags_to_resource(ResourceName=ID, Tags=[{'Key': Tag_Key, 'Value': Tag_Value}])
        except:
            return False, str(sys.exc_info())
        return True

    # Add tag to DynamoDB resource
    def dynamo(self, ID):
        '''
        ID = dynamodb ARN
        '''
        dynamo_client = session.client('dynamodb')
        try:
            dynamo_client.tag_resource(ResourceArn=ID, Tags=[{'Key': Tag_Key, 'Value': Tag_Value}])
        except:
            return False, str(sys.exc_info())
        return True

    # Add tag to EMR resource
    def emr(self, ID):
        '''
        ID = emr cluster ID
        '''
        emr_client = session.client('emr')
        try:
            emr_client.add_tags(ResourceId=ID, Tags=[{'Key': Tag_Key, 'Value': Tag_Value}])
        except:
            return False, str(sys.exc_info())
        return True

    # Add tag to Key Management Service resource
    def kms(self, ID):
        '''
        ID = key ID
        '''
        kms_client = session.client('kms')
        try:
            kms_client.tag_resource(KeyId=ID, Tags=[{'TagKey': Tag_Key, 'TagValue': Tag_Value}])
        except:
            return False, str(sys.exc_info())
        return True

    # Add tag to ElasticSearch resource
    def es(self, ID):
        '''
        ID = elastic search ARN
        '''
        es_client = session.client('es')
        try:
            es_client.add_tags(ARN=ID, TagList=[{'Key': Tag_Key, 'Value': Tag_Value}])
        except:
            return False, str(sys.exc_info())
        return True

    # Add tag to Elastic Container Service resource
    def ecs(self, ID):
        '''
        ID = cluster ARN
        '''
        ecs_client = session.client('ecs')
        try:
            ecs_client.tag_resource(resourceArn=ID, tags=[{'key': Tag_Key, 'value': Tag_Value}])
        except:
            return False, str(sys.exc_info())
        return True

    # Add tag to Elastic Kubernetes Service resource
    def eks(self, ID):
        '''
        ID = ARN
        '''
        eks_client = session.client('eks')
        try:
            eks_client.tag_resource(resourceArn=ITEM['arn'], tags={Tag_Key: Tag_Value})
        except:
            return False, str(sys.exc_info())
        return True

    # Add tag to Elastic Container Registry resource
    def ecr(self, ID):
        '''
        ID = repository ARN
        '''
        ecr_client = session.client('ecr')
        try:
            ecr_client.tag_resource(resourceArn=ID, tags=[{'Key': Tag_Key, 'Value': Tag_Value}])
        except:
            return False, str(sys.exc_info())
        return True

    # Add tag to Lambda resource
    def lam(self, ID):
        '''
        ID = lambda function ARN
        '''
        lam_client = session.client('lambda')
        try:
            lam_client.tag_resource(Resource=ID, Tags={Tag_Key: Tag_Value})
        except:
            return False, str(sys.exc_info())
        return True

    # Add tag to API Gateway resource
    def agw(self, ID):
        '''
        ID = gateway ARN
        '''
        agw_client = session.client('apigateway')
        try:
            agw_client.tag_resource(resourceArn=ID, tags={Tag_Key: Tag_Value})
        except:
            return False, str(sys.exc_info())
        return True

    # Add tag to API Gateway v2 resource
    def agw2(self, ID):
        '''
        ID = gateway ARN
        '''
        agw2_client = session.client('apigatewayv2')
        try:
            agw2_client.tag_resource(resourceArn=ID, tags={Tag_key: Tag_Value})
        except:
            return False, str(sys.exc_info())
        return True

    # Add tag to Simple Queue Service resource
    def sqs(self, ID):
        '''
        ID = Queue URL
        '''
        sqs_client = session.client('sqs')
        try:
            sqs_client.tag_queue(QueueUrl=ID, Tags={Tag_Key: Tag_Value})
        except:
            return False, str(sys.exc_info())
        return True

    # Add tag to Simple Notification Service resource
    def sns(self, ID):
        '''
        ID = Topic ARN
        '''
        sns_client = session.client('sns')
        try:
            sns_client.tag_resource(ResourceArn=ID, Tags=[{'Key': Tag_Key, 'Value': Tag_Value}])
        except:
            return False, str(sys.exc_info())
        return True

# Set up class to get tags from resource
class get_tags:

    def __init__(self, PROFILE, REGION, KEY, VALUE):
        self.Tag_Key = KEY
        self.Tag_Value = VALUE
        try
            self.session = boto3.Session(profile_name=PROFILE, region_name=REGION)
        except:
            print(sys.exc_info()[1])
            sys.exit(1)

    # get EC2 tags
    def ec2(self, ID, TAG = 'ALL'):
        '''
        ID = instance ID
        TAG = Tag key to get value for, use ALL to list all tag keys with values
        '''
        ec2_client = session.client('ec2')
        if TAG == 'ALL':
            try:
                Tag_List = ec2_client.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [ID]}])['Tags']
            except:
                return False, str(sys.exc_info())
            return True, Tag_List
        else:
            try:
                Tag_Value = ec2_client.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [ID]}, {'Name': 'key', 'Values': ['Name']}])[TAG][0]['Value']
            except:
                return False, str(sys.exc_info())
            return True, Tag_Value

    # get AutoScale Group tags
    def asg(self, ID, TAG = 'ALL'):
        '''
        ID = autoscale group ID
        TAG = Tag key to get value for, use ALL to list all tag keys with values
        '''
        asg_client = session.client('autoscaling')
        if TAG == 'ALL':
            try:
                Tag_List = asg_client.
