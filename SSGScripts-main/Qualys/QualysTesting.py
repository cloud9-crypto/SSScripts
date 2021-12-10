"""Get DAST scan results from Qualys"""

import json
import sys
import os
import requests

#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import qualysUser, qualysPass, qualysUrl

#define
scanid = "22935307"
reportid = "2145512"


headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "user": qualysUser,
    "password": qualysPass
}
url = '{0}/qps/rest/3.0/search/was/webapp'.format(qualysUrl)

resp = requests.post(url, headers=(headers))
results = resp.json()
print(resp)







#xmlorjson = 'xml'
xmlorjson = 'json'

url = '{0}/qps/rest/3.0/get/was/wasscan/{1}'.format(qualysUrl, scanid) #SCAN DETAILS
#url = '{0}/qps/rest/3.0/qps/rest/3.0/download/was/wasscan/{1}'.format(qualysUrl, scanid) #SCAN Results
#url = '{0}/qps/rest/3.0/download/was/report/{1}'.format(qualysUrl, reportid) #report
#url = '{0}/qps/rest/3.0/search/was/webapp'.format(qualysUrl) #/shrug

if xmlorjson == 'json':
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "user": qualysUser,
        "password": qualysPass
    }
elif xmlorjson == 'xml':
    headers = {
        "user": qualysUser,
        "password": qualysPass
    }

resp = requests.get(url, headers=(headers))
print(resp)
if xmlorjson == 'json':
    test = resp.json()
elif xmlorjson == 'xml':
    test=resp.content
    test2 = resp.text
print(test)


#get report
url = "{0}/qps/rest/3.0/search/was/report".format(qualysUrl)
resp = requests.post(url, headers=(headers))
if xmlorjson == 'json':
    test = resp.json()
    reports = resp.json()["ServiceResponse"]["data"]
elif xmlorjson == 'xml':
    test=resp.content 
    test2 = resp.text
print(resp)


for report in reports:
    url = '{0}/qps/rest/3.0/download/was/report/{1}'.format(qualysUrl, report["Report"]["id"])
    resp = requests.get(url, headers=(headers))
    result = resp.text
    print(resp)

