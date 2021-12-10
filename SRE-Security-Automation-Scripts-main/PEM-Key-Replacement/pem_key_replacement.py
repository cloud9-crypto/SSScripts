import boto3
import sys
import json
import time
import csv
import os
from collections import defaultdict
import paramiko
from botocore.exceptions import ClientError

environment = boto3.client('sts').get_caller_identity().get('Account')
ec2 = boto3.resource('ec2')

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

report_name = 'ssh_pem_key_replacement_report-' + environments[environment] + '.csv'
#check if report exist locally
exist_filepath = "{}".format(report_name)
if os.path.exists(exist_filepath):
    os.remove(exist_filepath)

field_names = [
    'account_name', 'instance_id', 'os_type', 'new_keypair_name', 'new_keypair_location', 'connection_status', 'updated_user_data_cleanup', 'added_new_tags'
]

ec2info = {}
instanceinfo = defaultdict()

#open  instances input list
filename = "sample_test_instance_list.csv"
with open(filename, mode='r') as infile:
        reader = csv.reader(infile)
        next(reader)
        for everyline in reader:
          ec2info[everyline[0]] = {'account_name':everyline[0], 'instance_id':everyline[1], 'os_type':everyline[2]}
          print('------------------------------------------------------------------------------------')
          for key, value in ec2info.items():
            serverID = ec2info[key]['instance_id']
            instance = ec2.Instance(serverID)
            osType = ec2info[key]['os_type']
            accountName = ec2info[key]['account_name']
            instanceinfo[instance.id] = {
                'PrivateIP': instance.private_ip_address
            }
            privateIP = instanceinfo[instance.id]['PrivateIP']
            accountName = "awsmmsandbox" #<account_name>, ex: awsmmsandbox
            local_key_path = "new_pem_keys/{}.pem".format(accountName)
            newPemKey = "{}.pem".format(accountName)
            newPemKeyLocation = "Vault: secrets/secret/SSH-Keys/{}-291086536081".format(accountName) #replace account number accordingly to account_name in line 83
            if osType == 'Ubuntu':
                loginUser = 'ubuntu'
            elif osType == 'Debian':
                loginUser = 'admin'
            else:
                loginUser = 'ec2-user'

            #stopping the instance
            status = instance.state['Name']
            if status == "running":
                print("xxxxxx stopping instance to update user data xxxxxx")
                stop_response = instance.stop(Hibernate=False, DryRun=False, Force=False)
                #wait until instance is stopped
                instance.wait_until_stopped()
                print("Instance {} is {}".format(serverID, instance.state['Name']))
            else:
                print("Instance {} already in stopped state".format(serverID))     
            
            #Update user data
            try:
                print("updating user data of instance...........:", serverID)
                user_data_file = open("user_data/{}_user_data.txt".format(loginUser), "r")
                user_data = user_data_file.read()
                user_data_update_response = instance.modify_attribute(
                    UserData={
                        'Value': '{}'.format(user_data)
                    }
                )
                time.sleep(10)
            except ClientError as e:
                print(e)
            print("user data update is Done......")

            #starting the instance
            if instance.state['Name'] == 'stopped':
                print("-_-_- starting instance -_-_-")
                start_response = instance.start(AdditionalInfo='Reserved', DryRun=False)
                #wait until instance is running
                instance.wait_until_running()
                print("Instance {} is {}".format(serverID, instance.state['Name']))   
            else:
                print("Instance {} already in started state".format(serverID))

            #SSH connection test with New PEM Key
            time.sleep(30)
            path = local_key_path
            if os.path.isfile(path):
                print ("PEM file exists, trying connection now")
                key = paramiko.RSAKey.from_private_key_file(local_key_path)
                connection = paramiko.SSHClient()
                connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                print ("connection in progress...")
                try:
                    print('Connecting with user', loginUser)
                    connection.connect(hostname=privateIP, username=loginUser, pkey=key)
                    if connection.get_transport().is_active() == True:
                        print('Connected with user:', loginUser)
                        connectionStatus = "SSH Connection Success with User {}".format(loginUser)
                        time.sleep(20)
                    else:
                        print('Unable to connect')
                        connectionStatus = "Unable to establish SSH connection"
                except Exception as error:
                    print(error)
                    connectionStatus = error
                    
            else:
                connectionStatus = "PEM Key {} not found locally in the path".format(newPemKey)

            if osType == "windows":
                connectionStatus = "Instance ID: {} is a Windows machine, Skipping ssh connection test, try RDP".format(serverID)
            
            #user data clean up - post new pem key update
            #stopping the instance
            if instance.state['Name'] == 'running':
                print("xxxxxx stopping instance for cleanup of updated user data xxxxxx")
                stop_response = instance.stop(Hibernate=False, DryRun=False, Force=False)
                #wait until instance is stopped
                instance.wait_until_stopped()
                print("Instance {} is {}".format(serverID, instance.state['Name']))
            else:
                print("Instance {} already in stopped state".format(serverID))   

            #Clear updated user data
            try:
                print("clearing updated user data...........:", serverID)
                user_data_clear_response = instance.modify_attribute(
                    UserData={
                        'Value': ''
                    }
                )
                time.sleep(10)
            except ClientError as e:
                print(e)

            #starting the instance
            if instance.state['Name'] == 'stopped':
                print("-_-_- starting instance -_-_-")
                start_response = instance.start(AdditionalInfo='Reserved', DryRun=False)
                #wait until instance is running
                instance.wait_until_running()
                print("Instance {} is {}".format(serverID, instance.state['Name']))   
            else:
                print("Instance {} already in started state".format(serverID))  

            cleanup_updated_user_data = "Yes"
            print("PEM Key replacement Done for instance {}".format(serverID))
            
            #adding new tags information
            add_tags = ec2.create_tags(Resources=['{}'.format(serverID)],
                Tags = [
                    {
                        'Key': 'pem-supportowner',
                        'Value': 'sreteam@massmutual.com'
                    },
                    {
                        'Key': 'new-keypair-name',
                        'Value': '{}'.format(newPemKey)
                    },
                    {
                        'Key': 'new-keypair-location',
                        'Value': '{}'.format(newPemKeyLocation)
                    }
                ]
            )
            addedNewTags = 'Yes'
            print("Added new Tags")

            #writing fields to report
            with open(report_name, 'a') as f:
                writer = csv.DictWriter(f, fieldnames=field_names)
                if f.tell() == 0:
                    writer.writeheader()
                row = {
                    'account_name': accountName,
                    'instance_id': serverID, 
                    'os_type': osType, 
                    'new_keypair_name': newPemKey, 
                    'new_keypair_location': newPemKeyLocation, 
                    'connection_status': connectionStatus, 
                    'updated_user_data_cleanup': cleanup_updated_user_data,
                    'added_new_tags': addedNewTags
                }
                writer.writerow(row)
print("PEM Key replacement Done for Account: {}".format(accountName))
