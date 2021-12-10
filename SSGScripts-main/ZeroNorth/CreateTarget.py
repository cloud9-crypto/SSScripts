#Creates a new target in ZeroNorth with the below details.  Adds Jira notification
"""Creates a new target in ZeroNorth with the below details.  Adds Jira notification"""

import sys
import os
import json
import requests


#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import zn_api_key, jiraid, jirakey, slackwebhook

#manual
name = "SSGDemo"
description = "Jira secret for {name}"
bu = "ECS"
pipeline = "SSG"
notificationsThreshold = 7
email = "pcagan@massmutual.com"
jiraprojectid = "SGP"
envid = "ZSmox7N2Sc63qUt4rldnfQ"
slackchannel = "ssg-testing"

#Create Jira secret
payloadjson = {
    "type": "jira",
    "secret": {
        "domain": "massmutual.atlassian.net",
        "projectId": jiraprojectid,
        "username": jiraid,
        "password": jirakey},
    "description": description
}

payload = json.dumps(payloadjson)
url = 'https://api.zeronorth.io/v1/secrets'
headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {0}'.format(zn_api_key)}
resp = requests.post(url, headers=headers, data=payload)
print(resp)
jirasecret = resp.json()["key"]

#create target json
newtargetjson = {
    "name": name,
    "environmentType": "artifact",
    "environmentId": envid,
    "parameters": {
        "name": name
        },
    "customerMetadata":{
        "BU":bu,
        "Pipeline":pipeline},
    "notificationsThreshold": notificationsThreshold,
    "notifications": [
        {
            "type": "email",
            "options": {"recipients": [email]}
        },
        {
        "type": "slack",
        "options": {
          "notify": [{
              "channel": slackchannel,
              "url": slackwebhook}]}
        },
        {
            "type": "jira",
            "options": {"notify": [{"secret": jirasecret}]}
        }]
}


# convert into JSON:
newtarget = json.dumps(newtargetjson)
url2 = 'https://api.zeronorth.io/v1/targets'
resp2 = requests.post(url2, headers=headers, data=newtarget)
print(resp2)
