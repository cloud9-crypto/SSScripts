import boto3
import csv
import json
import os.path
from collections import defaultdict
import paramiko

# 1. Collect all Running EC2 Instances information
# 2. Query all PEM Key file names that are associated with the EC2 Instance Ids that have been collected
# 3. Create a csv report all relevant information `field_names`

ec2 = boto3.resource('ec2')
client = boto3.client('autoscaling')
environment = boto3.client('sts').get_caller_identity().get('Account')

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

report_name = 'ssh_pem_key_information_report-' + environments[environment] + '.csv'

exist_filepath = "{}".format(report_name)
if os.path.exists(exist_filepath):
    os.remove(exist_filepath)

field_names = [
    'InstanceId', 'OSType', 'PrivateIP', 'SSHKeyName', 'PEM File Available', 'ASG_Status'
]

running_instances = ec2.instances.filter(Filters=[{
    'Name': 'instance-state-name',
    'Values': ['running']
}])

ec2info = defaultdict()
for instance in running_instances:
    ec2info[instance.id] = {
        'ID': instance.instance_id,
        'OSType': instance.platform,
        'PrivateIP': instance.private_ip_address,
        'SSHKeyName': instance.key_name,
        'PEM File Available': '',
        'ASG_Status': ''
    }
    instanceID = ec2info[instance.id]['ID']
    osType = ec2info[instance.id]['OSType']
    privateIP = ec2info[instance.id]['PrivateIP']
    instanceSSHKeyName = ec2info[instance.id]['SSHKeyName']
    asg_response = client.describe_auto_scaling_instances(InstanceIds=['{}'.format(instanceID)])
    asg_data = json.dumps(asg_response)
    asg_str = json.loads(asg_data)

    asg_check = asg_str['AutoScalingInstances']
    if asg_check == []:
        asg_status = "No"
    else:
        
        asg_inst = asg_response['AutoScalingInstances']
        asg_status = asg_inst[0]['AutoScalingGroupName']
    print(asg_status)
    
    if instanceSSHKeyName == None:
        connectionStatus = "Instance ID: {} - SSH Key pair is not attached".format(instanceID)
        pemFileAvailable = "No"
        print('------------------------')

    else:
        if instanceSSHKeyName.endswith('.pem'):
            updatedSSHKeyname = instanceSSHKeyName.strip('.pem')
        else:
            updatedSSHKeyname = instanceSSHKeyName

        path = "PEM/{}.pem".format(updatedSSHKeyname)

        if os.path.isfile(path):
            print ("PEM file exists, trying connection now")
            pemFileAvailable = "Yes"
            key_path = "PEM/{}.pem".format(updatedSSHKeyname)

            print(key_path)
            print(privateIP)
            # login_username = {'ubuntu', 'ec2-user', 'admin'}
            # key = paramiko.RSAKey.from_private_key_file(key_path)
            # connection = paramiko.SSHClient()
            # connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # print ("connection in progress...")
            # for user in login_username:
            #     try:
            #         print('Connecting with user', user)
            #         connection.connect(hostname=privateIP, username=user, pkey=key)
            #         print("Authentication status:",connection.get_transport().is_active())

            #         if connection.get_transport().is_active() == False:
            #             continue
            #         else:
            #             print('Connected with User:', user)
            #             connectionStatus = "SSH Connection Success with User {}".format(user)
            #             print('------------------------')
            #             break
            #     except Exception as error:
            #         print(error)
            #         connectionStatus = error
            #         print('------------------------')

        else:
            connectionStatus = "PEM Key {} not found locally in the path".format(instanceSSHKeyName)
            pemFileAvailable = "No"
            print('------------------------')
            
        if osType == "windows":
            connectionStatus = "Instance ID: {} is a Windows machine, Skipping ssh connection test, try RDP".format(instanceID)
            print('------------------------')
            
    status = connectionStatus
    pemAvailability = pemFileAvailable

    with open(report_name, 'a') as f:
        writer = csv.DictWriter(f, fieldnames=field_names)
        if f.tell() == 0:
            writer.writeheader()

        print(instanceID, status)
        row = {
            'InstanceId': instanceID, 
            'OSType': osType, 
            'PrivateIP': privateIP, 
            'SSHKeyName': instanceSSHKeyName,
            'PEM File Available': pemAvailability,
            'ASG_Status': asg_status
        }
        writer.writerow(row)

print("SSH PEM key validation Done for Account:", environments[environment])
