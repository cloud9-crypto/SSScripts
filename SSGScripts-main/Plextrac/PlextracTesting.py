"""Upload findings to Plextrac"""

import json
import sys
import os
import requests

#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import ptUser, ptPass,ptUrl

#vars
domain = ptUrl
clientID = "3531"
reportID = "500014"
idmClient = "570"
idmReport = "4461"

#Get auth token
authurl = "{0}/api/v1/authenticate".format(domain)
authpayload = {'username': ptUser, 'password': ptPass}
authpayload_json = json.dumps(authpayload)
authheaders = {'Content-Type': 'application/json'}
authresp = requests.request("POST", authurl, headers=authheaders, data=authpayload_json)
print(authresp)
respinfo = authresp.json()
token = authresp.json()["token"]



url = "https://massmutual.plextrac.com/api/v1/tenant/0/field-template/0"

payload = {}
headers = {
  'Authorization': '{0}'.format(token),
  'Content-Type': 'application/json'
}
response = requests.request("GET", url, headers=headers, data = payload)
result = response.json()
print(response.text.encode('utf8'))



url = "https://massmutual.plextrac.com/api/v1/tenant/0/field-templates"

payload = {}
headers = {
  'Authorization': '{0}'.format(token),
  'Content-Type': 'application/json'
}


response = requests.request("GET", url, headers=headers, data = payload)
result = response.json()
print(response.text.encode('utf8'))


url = "https://massmutual.plextrac.com/client/3531/report/500028/"

payload = {}
headers = {
  'Authorization': '{0}'.format(token),
  'Content-Type': 'application/json'
}

response = requests.request("GET", url, headers=headers, data = payload)
result = response.json()
print(response.text.encode('utf8'))


url = "https://massmutual.plextrac.com/client/3531/report/500028/flaw/1091051817"
url = "https://massmutual.plextrac.com/api/v1/tenant/field-templates"

payload = {}
headers = {
  'Authorization': '{0}'.format(token),
  'Content-Type': 'application/json'
}

response = requests.request("GET", url, headers=headers, data = payload)
result = response.json()
print(response.text.encode('utf8'))

url = "{0}/api/v1/client/{1}/report/{2}/flaws".format(domain, clientID, reportID)

payload = {}
headers = {
  'Authorization': '{0}'.format(token)
}

response = requests.request("GET", url, headers=headers, data = payload)
results = response.json()
print(response.text.encode('utf8'))


url = "{0}/api/v1/reports".format(domain)

payload = {}
files = {}
headers = {
  'Authorization': '{0}'.format(token)
}

response = requests.request("GET", url, headers=headers, data = payload, files = files)
results = response.json()
print(response.text.encode('utf8'))



url = "{0}/client/{1}/reports".format(domain, clientID)

payload = {}
headers = {
  'Authorization': '{0}'.format(token),
  'Content-Type': 'application/json'
}

response = requests.request("GET", url, headers=headers, data = payload)
results = response.json()
print(response.text.encode('utf8'))






#Get findings list
url = "{0}/api/v1/client/{1}/report/{2}/flaws".format(domain, clientID, reportID)
headers = {'Authorization': '{0}'.format(token)}
response = requests.request("GET", url, headers=headers)
results = response.json()
print(response.text.encode('utf8'))

#Create finding
url = "{0}/api/v1/client/{1}/report/{2}/flaw/create".format(domain, clientID, reportID)
payload = {
    'title': 'TEST3',
    'description': 'Description',
    'severity': 'Critical',
    'assignedTo': 'test@test.com',
    'status': 'Open',
    'source': 'source'
    }
files = [

]
headers = {
    'Authorization': token
}

response = requests.request("POST", url, headers=headers, data=payload, files=files)
results2 = response.json()
print(response.text.encode('utf8'))
