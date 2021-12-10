#Setup roles on Sonatype server
"""Setup roles on Sonatype server"""

import os
import sys
import requests

#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import stlabcred, stlabserver, stentcred, stentserver #fix later

#Define variables
user = 'admin' # pull from creds
password = 'ADMINPASSOWRD' # pull from creds
instanceurl = "SERVERURL" # pull from creds
org = "ORGID" # pull from creds?
usergroup = "fim-sonatype-enterprise"
admingroup = "fim-sonatype-admin"
orgurl = "{0}/api/v2/roleMemberships/organization/{1}".format(instanceurl, org)
globalurl = "{0}/api/v2/roleMemberships/global".format(instanceurl)
rolesurl = "{0}/api/v2/roles".format(instanceurl)

#get roles
resp = requests.get(rolesurl, auth=(user, password))
print(resp)
roles = resp.json()["roles"]

#find IDs
for x in roles:
    if x["name"] == usergroup:
        usergroupid = x["id"]
    elif x["name"] == "System Administrator":
        sysadmingroupid = x["id"]
    elif x["name"] == "Policy Administrator":
        policyadmingroupid = x["id"]

#Put sys admin role
sysadminurl = '{0}/api/v2/roleMemberships/global/role/{1}/group/{2}'.format(instanceurl, sysadmingroupid, admingroup)
resp2 = requests.put(sysadminurl, auth=(user, password))
print(resp2)

#Put policy admin role
policyadminurl = '{0}/api/v2/roleMemberships/global/role/{1}/group/{2}'.format(instanceurl, policyadmingroupid, admingroup)
resp2 = requests.put(sysadminurl, auth=(user, password))
print(resp2)

#Put user role
userurl = '{0}/api/v2/roleMemberships/organization/{1}/role/{2}/group/{3}'.format(instanceurl, org, usergroupid, usergroup)
resp3 = requests.put(userurl, auth=(user, password))
print(resp3)

print("DONE")
