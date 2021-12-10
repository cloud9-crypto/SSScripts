#Checks for bad policies in runstatistics endpoint
"""Checks for bad policies in runstatistics endpoint"""

import os
import sys
import requests

#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import zn_api_key

#define variables
token = zn_api_key
ctype = 'application/json'

#define endpoints
url = 'https://api.zeronorth.io/v1/policies?limit=1000000'
url2 = 'https://api.zeronorth.io/v1/reports/policyRunStatistics?groupByPolicy=true&limit=100&offset=0'
headers = {'Content-Type': ctype, 'Authorization': 'Bearer {0}'.format(token)}
headers2 = {'Content-Type': ctype,'Accept': ctype, 'Authorization': 'Bearer {0}'.format(token)}

#pull data
resp = requests.get(url, headers=headers)
print(resp)

#load data
znresults = resp.json()
zndata  = znresults[0]

#create list
policies = []
for policy in zndata:
    policies.append(policy["id"])

badpolicies = []

for entry in policies:
    #call api
    payload = '{"policyIds": ["%s"]}' % (entry)
    resp2 = requests.post(url2, headers=headers2, data=payload)
    
    #load data
    znresults2 = resp2.json()

    for target in znresults2:
        if znresults2[target]["targetId"] is None:
            print(znresults2[target]["policyId"])
            badpolicies.append(znresults2[target]["policyId"])

goodpolicies = len(policies)-len(badpolicies)
print("Bad policies")
print(len(badpolicies))
print("Good policies")
print(goodpolicies)
