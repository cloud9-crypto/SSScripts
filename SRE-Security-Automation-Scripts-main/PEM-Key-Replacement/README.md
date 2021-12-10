# Link to Confluence page 
    https://massmutual.atlassian.net/wiki/spaces/SRE/pages/4105410164/Automation+Script+for+keypair+pem+replacement+for+instances+across+AWS+accounts

## Automation Script for PEM Key replacement for instances which we do not hold the  keypairs(pem files) across AWS accounts

### This automation script helps replacing a user data of the instance from new keypair (publickey), verification of SSH connection with new keypair, updating new keypair information to instance tags and generating a report. 
### After updating the new keypair information and ssh connection verification, script will clean up the updated userdata

#### We will connect to each individual AWS account via sre-aws-helpers, by running command ```getAWSTempCredentials```

## Prerequisites: 

1. sre-aws-helpers set up
2. python installed
3. install packages via pip, refer requirements.txt (like boto3, csv, paramiko, os.path, defaultdict)
4. input_instance_list (csv file - holds list of instances csv file, refer sample_test_instance_list.csv; as per your input file name update  line 67 in script) 
5. new_pem_keys (folder - holds new keypair(pem) file to test the ssh connection)
6. user_data (folder - holds userdata file, refer attached txt file in the folder; replace filename > {user} with username(ex: ubuntu) and same in line 14 and add publickey of new keypair in line 16; Depending upon instances os types we need ec2-user, ubuntu, admin userdata files in this folder
7. python script (in same path as new_pem_keys folder) 

## Steps to Run Automation script
* step 1: run getAWSTempCredentials and select AWS account and role to connect
* step 2: run python script ```pem_key_replacement.py```

#### Script execution flow for each instance from provided input instances list
* stopping instance
* updating user data
* starting instance
* ssh connection test
* stopping instance
* clearup updated userdata to blank userdata
* starting instance
* updating tags

#### After successful PEM key replacement and verification, you will see below message on CLI
```PEM Key replacement Done for Account: <account name>```

#### Also, script will generate csv file (in same folder path where we have python script) with the information about account_name, instance_id, os_type, new_keypair_name, new_keypair_location, SSH Connection status, updated_user_data_cleanup and added_tags.
```ssh_pem_key_replacement_report-<account_name>.csv```
