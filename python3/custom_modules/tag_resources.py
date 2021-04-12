import boto3, botocore.exceptions, sys
from ast import literal_eval

Profile_Name = 'plume-dev-mfa'
Control_Key = 'costcenter'
Control_Value = 'r+d'
Create_String = f'Creating tag {Control_Key}:{Control_Value} for'
Region_List = ['us-west-1', 'us-west-2', 'us-east-1', 'us-east-2', 'ap-south-1', 'ap-northeast-1', 'ap-northeast-2', 'ap-northeast-3', 'ap-southeast-1', 'ap-southeast-2', 'ca-central-1', 'eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-north-1', 'sa-east-1']
Alternate_Region_List = ['af-south-1', 'ap-east-1', 'eu-south-1', 'me-south-1']

def set_session(PROFILE, REGION='us-west-2'):
    try:
        session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    except:
        print(sys.exc_info()[1])
        sys.exit(1)
    return session

def config_ec2_tags(REGION):
    ec2 = set_session(Profile_Name, REGION).client('ec2')
    config_service = set_session(Profile_Name, REGION).client('config')
    for ITEM in config_service.get_compliance_details_by_config_rule(ConfigRuleName='ec2-plume-dev-required-tags', ComplianceTypes=['NON_COMPLIANT'], Limit=20)['EvaluationResults']:
        Resource_ID = ITEM['EvaluationResultIdentifier']['EvaluationResultQualifier']['ResourceId']
        Costcenter_Value = ''
        for TAGS in ec2.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [Resource_ID]}])['Tags']:
            if TAGS['Key'] == 'costcenter':
                Costcenter_Value = TAGS['Value']
        if Costcenter_Value != 'r+d':
            print(f'\n', Resource_ID)
            print('Coscenter value is NOT r+d! Value: ', Costcenter_Value)
            print('Changing value to r+d...')
            ec2.create_tags(Resources=[Resource_ID], Tags=[{'Key': 'costcenter', 'Value': 'r+d'}])

def check_tags(IN, CONTROLK, CONTROLV):
    try:
        TAGS = IN['Tags']
    except KeyError:
        return False
    except:
        print('check_tags error:', sys.exc_info())
        sys.exit(1)
    else:
        if not TAGS:
            return False
        elif len(TAGS) < 1:
            return False
        elif CONTROLK in [X['Key'] for X in TAGS]:
            for X in TAGS:
                if X['Key'] == CONTROLK and X['Value'] == CONTROLV:
                    return True
    return False

def ec2_tags(REGION):

    ec2 = set_session(Profile_Name, REGION).client('ec2')

    def create_tag(ID, CONTROLK, CONTROLV):
        print('Creating tag', CONTROLK + ':' + CONTROLV, 'for', ID)
        try:
            ec2.create_tags(Resources=[ID], Tags=[{'Key': CONTROLK, 'Value': CONTROLV}])
        except:
            print(sys.exc_info())
        else:
            print('Done.')

#    print('ec2 instances in', REGION)
#    for ITEM in ec2.describe_instances()['Reservations']:
#        for ID in ITEM['Instances']:
#            Instance_ID = ID['InstanceId']
#        if not check_tags(ID, Control_Key, Control_Value):
#            create_tag(Instance_ID, Control_Key, Control_Value)
    print('ec2 customer gateways in', REGION)
    for ITEM in ec2.describe_customer_gateways()['CustomerGateways']:
        if not check_tags(ITEM, Control_Key, Control_Value):
            create_tag(ITEM['CustomerGatewayId'], Control_Key, Control_Value)
    print('ec2 nat gateways in', REGION)
    for ITEM in ec2.describe_nat_gateways()['NatGateways']:
        if not check_tags(ITEM, Control_Key, Control_Value):
            create_tag(ITEM['NatGatewayId'], Control_Key, Control_Value)
    print('ec2 ebs volumes in', REGION)
    for ITEM in ec2.describe_volumes()['Volumes']:
        if not check_tags(ITEM, Control_Key, Control_Value):
            create_tag(ITEM['VolumeId'], Control_Key, Control_Value)
    print('ec2 elastic IP addresses in', REGION)
    for ITEM in ec2.describe_addresses(PublicIps=[])['Addresses']:
        if not check_tags(ITEM, Control_Key, Control_Value):
            create_tag(ITEM['AllocationId'], Control_Key, Control_Value)
#    print('ec2 snapshots in', REGION)
#    for ITEM in ec2.describe_snapshots()['Snapshots']:
#        if 'Tags' in ITEM:
#            if not check_tags(ITEM, Control_Key, Control_Value):
#                create_tag(ITEM['SnapshotId'], Control_Key, Control_Value)
#        else:
#            create_tag(ITEM['SnapshotId'], Control_Key, Control_Value)
    print('ec2 images in', REGION)
    for ITEM in ec2.describe_images(Owners=['self'])['Images']:
        if not check_tags(ITEM, Control_Key, Control_Value):
            create_tag(ITEM['ImageId'], Control_Key, Control_Value)
    print('ec2 launch templates in', REGION)
    for ITEM in ec2.describe_launch_templates()['LaunchTemplates']:
        if not check_tags(ITEM, Control_Key, Control_Value):
            create_tag(ITEM['LaunchTemplateId'], Control_Key, Control_Value)
    print()

def s3_tags():
    s3 = set_session(Profile_Name).client('s3')
    tag = set_session(Profile_Name).client('resourcegroupstaggingapi')

    print('s3 buckets')
    def tag_s3(ID, CONTROLK, CONTROLV):
        print(Create_String, ID)
        try:
#            s3.put_bucket_tagging(Bucket=ID, Tagging={'TagSet': [{'Key': CONTROLK, 'Value': CONTROLV}]})
            tag.tag_resources(ResourceARNList=[ID], Tags={Control_Key: Control_Value})
        except botocore.exceptions.ClientError as error:
            print('s3 tag error:', ID, CONTROLK, CONTROLV)
            print(error.response['Error']['Code'])
        except:
            print(sys.exc_info())
        else:
            print('Done.')

    for ITEM in s3.list_buckets()['Buckets']:
        ARN = f'arn:aws:s3:::{ITEM["Name"]}'
        try:
            TAGS = {'Tags': s3.get_bucket_tagging(Bucket=ITEM['Name'])['TagSet']}
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'NoSuchTagSet':
                tag_s3(ARN, Control_Key, Control_Value)
        except:
            print(sys.exc_info())
        else:
            if not check_tags(TAGS, Control_Key, Control_Value):
                tag_s3(ARN, Control_Key, Control_Value)

def asg_tags(REGION):
    asg = set_session(Profile_Name, REGION).client('s3')

    print('auto scaling groups in', REGION)
    def tag_asg(ID, CONTROLK, CONTROLV):
        print(Create_String, ID)
        try:
            asg.create_or_update_tags(Tags=[{'ResourceId': ID, 'Key': CONTROLK, 'Value': CONTROLV}])
        except botocore.exceptions.ClientError as error:
            print(error.response['Error']['Code'])
        except:
            print(sys.exc_info())
        else:
            print('Done.')

    for ITEM in s3.describe_auto_scaling_groups()['AutoScalingGroups']:
        if not check_tags(ITEM, Control_Key, Control_Value):
            tag_asg(ITEM['AutoScalingGroupName'], Control_Key, Control_Value)

def ddb_tags(REGION):
    ddb = set_session(Profile_Name, REGION).client('docdb')

    print('DocumentDB clusters and instances in', REGION)
    def tag_ddb(ID, CONTROLK, CONTROLV):
        print(Create_String, ID)
        try:
            ddb.add_tags_to_resource(ResourceName=ID, Tags=[{'Key': CONTROLK, 'Value': CONTROLV}])
        except botocore.exceptions.ClientError as error:
            print(error.response['Error']['Code'])
        except:
            print(sys.exc_info())
        else:
            print('Done.')

    def get_tags(ID):
        try:
            TAGS = {'Tags': ddb.list_tags_for_resource(ResourceName=ID)['TagList']}
        except botocore.exceptions.ClientError as error:
            TAGS = {'Tags': ''}
        return TAGS
            
    for ITEM in ddb.describe_db_clusters()['DBClusters']:
        ID = ITEM['DBClusterIdentifier']
        ARN = ITEM['DBClusterArn']
        TAGS = get_tags(ID)
        if not check_tags(TAGS, Control_Key, Control_Value):
            tag_ddb(ARN, Control_Key, Control_Value)
    for ITEM in ddb.describe_db_instances()['DBInstances']:
        ID = ITEM['DBInstanceIdentifier']
        TAGS = get_tags(ID)
        if not check_tags(TAGS, Control_Key, Control_Value):
            tag_ddb(ARN, Control_Key, Control_Value)

def rds_tags(REGION):
    rds = set_session(Profile_Name, REGION).client('rds')

    print('RDS clusters and instances in', REGION)
    def tag_rds(ID, CONTROLK, CONTROLV):
        print(Create_String, ID)
        try:
            rds.add_tags_to_resource(ResourceName=ID, Tags=[{'Key': CONTROLK, 'Value': CONTROLV}])
        except botocore.exceptions.ClientError as error:
            print(error.response['Error']['Code'])
        except:
            print(sys.exc_info())
        else:
            print('Done.')

    for ITEM in rds.describe_db_clusters()['DBClusters']:
        TAGS = {'Tags': ITEM['TagList']}
        if not check_tags(TAGS, Control_Key, Control_Value):
            tag_rds(ITEM['DBClusterArn'], Control_Key, Control_Value)
    for ITEM in rds.describe_db_instances()['DBInstances']:
        TAGS = {'Tags': ITEM['TagList']}
        if not check_tags(TAGS, Control_Key, Control_Value):
            tag_rds(ITEM['DBInstanceArn'], Control_Key, Control_Value)

def elb_tags(REGION):
    elb = set_session(Profile_Name, REGION).client('elbv2')

    print('ELB in', REGION)
    for ITEM in elb.describe_load_balancers()['LoadBalancers']:
        ARN = ITEM['LoadBalancerArn']
        TAGS = elb.describe_tags(ResourceArns=[ARN])['TagDescriptions'][0]
        if not check_tags(TAGS, Control_Key, Control_Value):
            print(Create_String, ARN)
            try:
                elb.add_tags(ResourceArns=[ARN], Tags=[{'Key': Control_Key, 'Value': Control_Value}])
            except botocore.exceptions.ClientError as error:
                print(error.response['Error']['Code'])
            except:
                print(sys.exc_info())
            else:
                print('Done.')

def emr_tags(REGION):
    emr = set_session(Profile_Name, REGION).client('emr')

    print('EMR in', REGION)
    for ITEM in emr.list_clusters()['Clusters']:
        TAGS = emr.describe_cluster(ClusterId=ITEM['Id'])['Cluster']['Tags']
        if not check_tags(TAGS, Control_Key, Control_Value):
            print(Create_String, ITEM['Id'])
            try:
                emr.add_tags(ResourceId=ITEM['Id'], Tags=[{'Key': Control_Key, 'Value': Control_Value}])
            except botocore.exceptions.ClientError as error:
                print(error.response['Error']['Code'])
            except:
                print(sys.exc_info())
            else:
                print('Done.')

def kms_tags(REGION):
    kms = set_session(Profile_Name, REGION).client('kms')

    print('KMS in', REGION)
    for ITEM in kms.list_keys()['Keys']:
        try:
            TAGS = literal_eval(str(kms.list_resource_tags(KeyId=ITEM['KeyId'])).replace('TagKey', 'Key').replace('TagValue', 'Value'))
        except botocore.exceptions.ClientError as error:
            print(error.response['Error']['Code'])
        except:
            print(sys.exc_info())
        else:
            TAGS = {}
        if not check_tags(TAGS, Control_Key, Control_Value):
            print(Create_String, ITEM['KeyId'])
            try:
                kms.tag_resource(KeyId=ITEM['KeyId'], Tags=[{'TagKey': Control_Key, 'TagValue': Control_Value}])
            except botocore.exceptions.ClientError as error:
                print(error.response['Error']['Code'])
            except:
                print(sys.exc_info())
            else:
                print('Done.')

def dynamo_tags(REGION):
    dynamo = set_session(Profile_Name, REGION).client('dynamodb')

    print('DynamoDB in', REGION)
    for NAME in dynamo.list_tables()['TableNames']:
        ARN = dynamo.describe_table(TableName=NAME)['Table']['TableArn']
        TAGS = dynamo.list_tags_of_resource(ResourceArn=ARN)
        if not check_tags(TAGS, Control_Key, Control_Value):
            print(Create_String, ARN)
            try:
                dynamo.tag_resource(ResourceArn=ARN, Tags=[{'Key': Control_Key, 'Value': Control_Value}])
            except botocore.exceptions.ClientError as error:
                print(error.response['Error']['Code'])
            except:
                print(sys.exc_info())
            else:
                print('Done.')

def es_tags(REGION):
    es = set_session(Profile_Name, REGION).client('es')

    print('ElasticSearch in', REGION)
    for NAME in es.list_domain_names()['DomainNames']:
        ID = es.describe_elasticsearch_domain(DomainName=NAME['DomainName'])['DomainStatus']['ARN']
        TAGS = {'Tags': es.list_tags(ARN=ID)['TagList']}
        if not check_tags(TAGS, Control_Key, Control_Value):
            print(Create_String, ID)
            try:
                es.add_tags(ARN=ID, TagList=[{'Key': Control_Key, 'Value': Control_Value}])
            except botocore.exceptions.ClientError as error:
                print(error.response['Error']['Code'])
            except:
                print(sys.exc_info())
            else:
                print('Done.')
            
def ecs_tags(REGION):
    ecs = set_session(Profile_Name, REGION).client('ecs')
    eks = set_session(Profile_Name, REGION).client('eks')
    ecr = set_session(Profile_Name, REGION).client('ecr')

    def gen_tags(ITEM):
        TAGS = {'Tags': []}
        if len(ITEM['tags']) < 1:
            TAGS['Tags'] += {}
        else:
            for T in ITEM['tags'].items():
                TAGS['Tags'].append({'Key': T[0], 'Value': T[1]})
        return TAGS

    print('ECS in', REGION)
    for ITEM in ecs.describe_clusters()['clusters']:
        TAGS = gen_tags(ITEM)
        if not check_tags(TAGS, Control_Key, Control_Value):
            print(Create_String, ITEM['clusterArn'])
            try:
                ecs.tag_resource(resourceArn=ITEM['clusterArn'], tags=[{'key': Control_Key, 'value': Control_Value}])
            except botocore.exceptions.ClientError as error:
                print(error.response['Error']['Code'])
            except:
                print(sys.exc_info())
            else:
                print('Done.')
    for NAME in eks.list_clusters()['clusters']:
        ITEM = eks.describe_cluster(name=NAME)['cluster']
        TAGS = gen_tags(ITEM)
        if not check_tags(TAGS, Control_Key, Control_Value):
            print(Create_String, NAME)
            try:
                eks.tag_resource(resourceArn=ITEM['arn'], tags={Control_Key: Control_Value})
            except botocore.exceptions.ClientError as error:
                print(error.response['Error']['Code'])
            except:
                print(sys.exc_info())
            else:
                print('Done.')
    for ITEM in ecr.describe_repositories()['repositories']:
        TAGS = {'Tags': ecr.list_tags_for_resource(resourceArn=ITEM['repositoryArn'])['tags']}
        if not check_tags(TAGS, Control_Key, Control_Value):
            print(Create_String, ITEM['repositoryName'])
            try:
                ecr.tag_resource(resourceArn=ITEM['repositoryArn'], tags=[{'Key': Control_Key, 'Value': Control_Value}])
            except botocore.exceptions.ClientError as error:
                print(error.response['Error']['Code'])
            except:
                print(sys.exc_info())
            else:
                print('Done.')

def lambda_tags(REGION):
    lam = set_session(Profile_Name, REGION).client('lambda')

    print('Lambda functions in', REGION)
    for ITEM in lam.list_functions()['Functions']:
        TAGS = {'Tags': []}
        for I in lam.list_tags(Resource=ITEM['FunctionArn'])['Tags'].items():
            TAGS['Tags'].append({'Key': I[0], 'Value': I[1]})
        if not check_tags(TAGS, Control_Key, Control_Value):
            print(Create_String, ITEM['FunctionName'])
            try:
                lam.tag_resource(Resource=ITEM['FunctionArn'], Tags={Control_Key: Control_Value})
            except botocore.exceptions.ClientError as error:
                print(error.response['Error']['Code'])
            except:
                print(sys.exc_info())
            else:
                print('Done.')

#def apigw_tags(REGION):
#    apigw = set_session(Profile_Name, REGION).client('apigateway')
#    apigwv2 = set_session(Profile_Name, REGION).client('apigatewayv2')
#
#    print('API Gateway in', REGION)
#    
#    for ITEM in apigw.get_rest_apis()['items']:
#        response = False
#        try:
#            TAGS = ITEM['tags']
#        except KeyError:
#            response = False
#        except:
#            print(sys.exc_info())
#            continue
#        else:
#            if Control_Key in TAGS:
#                if TAGS[Control_Key] == Control_Value:
#                    response = True
#        if not response:
#            try:
#                apigw.tag_resource(resourceArn=

def sqs_tags(REGION):
    sqs = set_session(Profile_Name, REGION).client('sqs')

    print('SQS in', REGION)
    try:
        URLS = sqs.list_queues()['QueueUrls']
    except KeyError:
        print('No Queues!')
    else:
        for ITEM in URLS:
            TAGS = {'Tags': []}
            for I in sqs.list_queue_tags(QueueUrl=ITEM)['Tags'].items():
                TAGS['Tags'].append({'Key': I[0], 'Value': I[1]})
            if not check_tags(TAGS, Control_Key, Control_Value):
                print(Create_String, ITEM)
                try:
                    sqs.tag_queue(QueueUrl=ITEM, Tags={Control_Key: Control_Value})
                except botocore.exceptions.ClientError as error:
                    print(error.response['Error']['Code'])
                except:
                    print(sys.exc_info())
                else:
                    print('Done.')

def sns_tags(REGION):
    sns = set_session(Profile_Name, REGION).client('sns')

    print('SNS in', REGION)
    for ITEM in sns.list_topics()['Topics']:
        TAGS = sns.list_tags_for_resource(ResourceArn=ITEM['TopicArn'])
        if not check_tags(TAGS, Control_Key, Control_Value):
            print(Create_String, ITEM['TopicArn'])
            try:
                sns.tag_resource(ResourceArn=ITEM['TopicArn'], Tags=[{'Key': Control_Key, 'Value': Control_Value}])
            except botocore.exceptions.ClientError as error:
                print(error.response['Error']['Code'])
            except:
                print(sys.exc_info())
            else:
                print('Done.')

for REGION in Region_List:
#    ec2 = set_session(Profile_Name, REGION).client('ec2')
#    try:
#        ec2.describe_instances(DryRun=True)
#    except botocore.exceptions.ClientError as error:
#        if error.response['Error']['Code'] == 'DryRunOperation':
#            print(REGION)
#            continue
#        print(REGION, 'FAILED!')
#        continue
#    print(REGION)
    ec2_tags(REGION)
    ddb_tags(REGION)
    rds_tags(REGION)
    elb_tags(REGION)
    kms_tags(REGION)
    dynamo_tags(REGION)
    es_tags(REGION)
    ecs_tags(REGION)
    lambda_tags(REGION)
    sqs_tags(REGION)
    sns_tags(REGION)

s3_tags()
