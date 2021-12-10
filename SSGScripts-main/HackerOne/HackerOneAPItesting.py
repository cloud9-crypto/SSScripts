"""HackerOne API testing"""

#https://api.hackerone.com/core-resources/#reports-get-all-reports

import sys
import os
import requests

#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import hackerOneUser, hackerOneApiKey


url = 'https://api.hackerone.com/v1/reports?filter%5Bprogram%5D%5B%5D=massmutual-h1c'
auth = (hackerOneUser, hackerOneApiKey)
ctype = 'application/json'
headers = {'Content-Type': ctype}

resp = requests.get(url, headers=headers, auth=auth)
print(resp)
hojson = resp.json()["data"]
print(hojson)
