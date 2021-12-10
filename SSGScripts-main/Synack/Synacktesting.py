"""Synack testing"""

import json
import sys
import os
import requests

#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import synToken


headers = {'Authorization': 'Bearer {0}'.format(synToken)}
#params = { "page[size]": 5, "page[number]": 2, "filter[search]": "XSS", "filter[updated_since]": "2021-02-11T00:25:43Z", "filter[status_id][]": [1, 2] }
params = { "filter[search]": "ATLASHORNET"}

# return 5 vulnerabilities (on page 2) updated since 2021-02-11T00:25:43Z (sorted by the resolved_at timestamp) with vulnerability status ID of 1 or 2 containing the term 'XSS'
url3 = "https://api.synack.com/v1/vulnerabilities"


resp3 = requests.get(url3, headers=headers, params=params, verify=False)
print(resp3)
results3 = resp3.json()
print(results3)




url = "https://api.synack.com/v1/assessments"
resp = requests.get(url, headers=headers, verify=False)

print(resp)
results = resp.json()
print(results)

assesmentid = "kalgdk75s1"
url2 = "https://api.synack.com/v1/assessments/{0}".format(assesmentid)
resp2 = requests.get(url2, headers=headers, verify=False)
print(resp2)
results2 = resp2.json()
print(results2)







#try:
#  r.raise_for_status()
#  print r.json() # parse JSON payload
#except requests.exceptions.HTTPError as e:
#  print e.message

