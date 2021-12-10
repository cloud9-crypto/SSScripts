
import sys
import os
import requests


#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import snyk

group = "46cb04da-4e9f-4cf7-b0ad-1f1811c8592d"

url = 'https://snyk.io/api/v1/group/{0}/members'.format(group)
auth = "token {0}".format(snyk)
headers = {"Authorization": auth, "Content-Type":"application/json; charset=utf-8"}

resp = requests.get(url, headers=headers)
results = resp.json()
print(resp)
for result in results:
    user = "{0}   |   {1}".format(result["name"],result["email"])
    print(user)