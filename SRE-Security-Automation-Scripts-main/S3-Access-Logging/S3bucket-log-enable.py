from logging import error
import boto3
import sys
import json
import time
import csv
import os
from collections import defaultdict
import paramiko
from botocore.exceptions import ClientError
from datetime import datetime

environment = boto3.client('sts').get_caller_identity().get('Account')
print (environment)
client = boto3.client('s3')
s3 = boto3.resource('s3')
session = boto3.session.Session()
s3_client = session.client('s3')

#Get total bucket list count
bucket_list = [bucket.name for bucket in s3.buckets.all()]
print ("Total S3 buckets:", len(bucket_list))
#print (bucket_list)

#Define the file headers
field_names = [
    'account_name', 'account_id', 'Bucket-name', 'Log-enabled(Yes/No)', 'Enabled-log,in-case-of-No', 'Comments'
]

#Function to create S3 bucket (to store cloudtrail logs)
def create_bucket(bucket_name, region):
    # Create bucket
    try:
        if region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
            print ('Bucket-',bucket_name,' created successfully!')
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,CreateBucketConfiguration=location)
            print ('Bucket-',bucket_name,' created successfully!')
    except ClientError as e:
        #logging.error(e)
        print (e)
        return False
    return True

#Function to grant ACL permission to log bucket
def grantaclBucket(s3_client,sourcebucket,targetbucket):
    try:
        acl = s3_client.get_bucket_acl(Bucket = sourcebucket)
        #print (acl)
        for d in acl['Grants']:
            if 'ID' in d['Grantee']: # If Grantee is NOT URI, then specific Grant needs to be given before enabling Logging
                canonical_id = d['Grantee']['ID']
                print (canonical_id)
                response = s3_client.put_bucket_acl(
                    AccessControlPolicy={
                        'Grants': [
                            {
                                'Grantee': {
                                    'Type': 'Group',
                                    'URI': 'http://acs.amazonaws.com/groups/s3/LogDelivery'
                                },
                                'Permission': 'READ_ACP'
                            },
                            {
                                'Grantee': {
                                    'Type': 'Group',
                                    'URI': 'http://acs.amazonaws.com/groups/s3/LogDelivery'
                                },
                                'Permission': 'WRITE'
                            }
                        ],
                        'Owner': {
                            'ID': canonical_id
                            },
                        },
                        Bucket=targetbucket
                    )
            elif 'URI' in d['Grantee']: # If Grant is already given to URL, no need of explicit Grant
                print("Log Delivery Group has the required permission...")
        return True
    except Exception as error:
        logging.error(e)
        return None

#Check S3 log bucket exits
defaultLogBucket = 'aws-logs-' + environment + '-us-east-1'
#print (defaultLogBucket)
if defaultLogBucket in bucket_list:
    print ('Default log bucket exists')
    #my_bucket = s3bucket.Bucket(bucketName)
else:
    print ('Default log bucket NOT exists. To be created')
    #call create bucket function
    create_bucket(defaultLogBucket,None)

#Check ACL is enabled for logging in the default log bucket
# bucket_logging = s3.BucketLogging(defaultLogBucket)
# bucket_logging_response = bucket_logging.logging_enabled
# if bucket_logging.logging_enabled is None:
#     print("Bucket - {} is not loggging Enabled" .format(defaultLogBucket))
#     print("Bucket - {} logging is in progress..." .format(defaultLogBucket))
grantaclBucket(s3_client,defaultLogBucket,defaultLogBucket) # Grant ACL to Log Delivery Group - mandatory before enabling logging
# else:
#     print("Bucket logging already enabled")

environments = {
'978856520288': 'qmprd',
'241741580507': 'apipnprd',
'649947276062': 'ceclnprd',
'887019692477': 'cxcloudsecmgr',
'706172495145': 'cxmgmtsre',
'528214016699': 'datasciencenon-prod',
'974445929406': 'datascienceproduction',
'340827108577': 'digital',
'060971710002': 'dxsnd',
'797547788689': 'evadata',
'208980661840': 'evadataprod',
'812537615333': 'htanprd',
'160360528757': 'liferiskmanagementprod',
'133316517682': 'liferisknonprod',
'224046922024': 'liferiskprod',
'352341246311': 'mm enterprise',
'255641612753': 'mmextendeddcsandbox',
'291086536081': 'mmsandbox',
'708724807854': 'preprod',
'630071356335': 'production',
'978856520288': 'qmsandbox',
'842140813730': 'sandboxpot',
'028409122053': 'sndrdev',
'839462916189': 'snowplownprd',
'458552773835': 'snowplowproduction',
'027721581419': 'sresnd',
'116115123301': 'strenprd',
'896850573825': 'streprd',
'645204690875': 'wpproduction',
'545119042404': 'wpsnonprod',
'184841865213': 'AWSSAPNon-Prod',
'715893564835': 'AWSSAPProd',
'709190732428': 'MM CX Non-Production',
'521314321012': 'MM CX Production',
'635464365399': 'cecl-dev',
'686561647649': 'mmawsmarketrisk'
}

#Define output filename with date and timestamp
report_name = 'S3LogEnable-' + environments[environment] + '-' + str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S')) + '.csv'
print(report_name)

#Create file and write headers
with open(report_name,'a') as f:
    writer = csv.DictWriter(f,fieldnames=field_names)
    if f.tell() == 0:
        writer.writeheader()

#Access each S3 bucket in a loop to verify the access logging enabled
bucket_list = [bucket.name for bucket in s3.buckets.all()]
for bucket in s3.buckets.all():
    print(bucket.name)
    #response = s3_client.get_bucket_logging(Bucket=bucket.name,)
    try:
        response = s3.BucketLogging(bucket.name)
        iniAccessEnabled = False
        finalAccessEnabled = None
        output = None
        if not response.logging_enabled:
            print ("Access logging to be enabled")  

            response.put(
            Bucket = bucket.name,
            BucketLoggingStatus={
                'LoggingEnabled': {
                    'TargetBucket': defaultLogBucket,
                    'TargetPrefix': 's3bucketlogs/'
                    }
                }
            )
            finalAccessEnabled = True
        else:
            iniAccessEnabled = True
            print ("Access logging already enabled")

    except Exception as e:
        output = "error:" + str(e)
        print(e)

    with open(report_name,'a') as f:
        writer = csv.DictWriter(f, fieldnames=field_names)
        row = {
            'account_name': environments[environment],
            'account_id': environment, 
            'Bucket-name': bucket.name, 
            'Log-enabled(Yes/No)': iniAccessEnabled, 
            'Enabled-log,in-case-of-No': finalAccessEnabled,
            'Comments': output
            }
        writer.writerow(row)

print("End of program")
