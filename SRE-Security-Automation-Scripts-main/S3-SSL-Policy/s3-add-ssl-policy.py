import boto3
import os
import botocore

# Define constant variables
default_policy_file_name = 'default_bucket_policy.json'
bucket_policy_file_name = 'bucket_policy.json'
default_bucket_keyword = 'DOC-EXAMPLE-BUCKET'
access_denied_buckets = []
empty_policy_buckets = []
s3 = boto3.resource('s3')


# Function that creates targeted bucket policy out of default bucket policy
def create_bucket_policy(bucket_name):
    default_policy_file = open(default_policy_file_name, 'r')
    bucket_policy_file = open(bucket_policy_file_name, 'x')
    policy_data = default_policy_file.read()
    bucket_policy_file.write(policy_data.replace(default_bucket_keyword, bucket_name))
    default_policy_file.close()
    bucket_policy_file.close()

# Return the content from the freshly created bucket policy file

def read_bucket_policy_file():
    bucket_policy_file = open(bucket_policy_file_name, 'r')
    file_content = bucket_policy_file.read()
    bucket_policy_file.close()
    return file_content

# Function should remove an already existent bucket policy file - cleanup    
def remove_policy_file():
    if os.path.isfile(bucket_policy_file_name):
        os.remove(bucket_policy_file_name)
    else:
        print(bucket_policy_file_name + "was not found to be deleted.")

# Create a file containing all the buckets with refused access.

def write_denied_access_buckets():
    if len(access_denied_buckets) == 0 :
        return
    access_denied_buckets_file = open("access_denied_buckets.txt", "w")
    for bucket in access_denied_buckets:
        access_denied_buckets_file.write(bucket + '\n')
    access_denied_buckets_file.close()

# Function that retrieves all s3 buckets as list
def aws_retrieve_buckets():
    all_buckets = []
    for bucket_data in boto3.client('s3').list_buckets()['Buckets']:
        all_buckets.append(bucket_data['Name'])
    return all_buckets

# Function that creates two separate lists:
# one with buckets with empty policy and 
# another with ones where the access is denied

def aws_return_bucket_policy(bucket_name):
    try:
        _ = s3.BucketPolicy(bucket_name).policy
    except botocore.exceptions.ClientError as error:
        error_code = error.response['Error']['Code']
        if error_code == "NoSuchBucketPolicy":
            empty_policy_buckets.append(bucket_name)
        if error_code == "IllegalLocationConstraintException":
            print('Bucket with name <' + bucket_name + "> does not exist!")
            return
        if error_code == "AccessDenied":
            access_denied_buckets.append(bucket_name)

# Function that modifies target bucket policy with 
# one similar to the default policy file.

def aws_modify_policy(bucket_name):
    ssl_policy = read_bucket_policy_file()
    try:
        result = s3.BucketPolicy(bucket_name).put(
            Policy = ssl_policy
        )
    except botocore.exceptions.ClientError as error:
        print(bucket_name)
        print(error)

def modify_all_empty_policies():
    for bucket_name in aws_retrieve_buckets():
        aws_return_bucket_policy(bucket_name)
    for empty_policy_bucket in empty_policy_buckets:
        create_bucket_policy(empty_policy_bucket)
        aws_modify_policy(empty_policy_bucket)
        remove_policy_file()
    write_denied_access_buckets()

modify_all_empty_policies()
    

