import json
import requests
import sys, os
import pymysql.cursors


#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import sjcttoken, sjtoken, sjenurl, sjusersurl, sjctenurl, sjctusersurl

#tokens
token = sjtoken
cttoken = sjcttoken

#headers
ctype = 'application/json'
headers = {'Content-Type': ctype,'ApiKey': token}
ctheaders = {'Content-Type': ctype,'ApiKey': cttoken}

#urls
enurl = sjenurl
usersurl = sjusersurl
ctenurl = sjctenurl
ctusersurl = sjctusersurl

#aband
resp = requests.get(ctenurl, headers=ctheaders)
results = resp.json()["path_enrollments"]

for result in results:
    if result["status"] == "abandoned" and result["level_name"] == "White Belt":
        print(result["email"] + " | " + result["level_name"] + " | " + result["status"])
print(resp)
