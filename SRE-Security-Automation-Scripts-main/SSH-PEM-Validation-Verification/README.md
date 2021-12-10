# Link to Confluence page 
    https://massmutual.atlassian.net/wiki/spaces/SRE/pages/3963388420/Automation+Script+for+PEM+Key+Validation+and+Verification+across+AWS+accounts

## Automation Script for PEM Key Validation and Verification across AWS accounts
### This automation script helps finding out PEM key attached to each running instance in the AWS account, validating the key exist in local PEM key folder and verification of SSH connection.

#### We will connect to each individual AWS account via sre-aws-helpers, by running command ```getAWSTempCredentials```

## Prerequisites: 

1. sre-aws-helpers set up
2. python installed
3. install packages via pip (like boto3, csv, paramiko, os.path, defaultdict)
4. PEM (folder - holds all pem files to validate and connect)
5. python script (in same path as PEM folder) 

## Steps to Run Automation script
* step 1: run getAWSTempCredentials and select AWS account and role to connect
* step 2: run python script ```python3 ssh-pem-key-validation-verification.py```

#### After successful PEM key validation and verification, you will see below message on CLI
```SSH PEM key validation Done for Account: <account name>```

### Also, script will generate csv file (in same folder path where we have PEM and python script) with the information about running instances, PEM File availability and SSH Connection status.
