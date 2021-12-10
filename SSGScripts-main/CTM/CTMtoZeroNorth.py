"""Pull applications from CTM and add to ZeroNorth"""

import sys
import os
import json
import requests
from requests.auth import HTTPBasicAuth

#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import ctmEndpoint, ctmUserId, ctmSecret, ctmOauthBase, ctmQueryBase, ctmAppQuery, ctmUtilQuery, znSandbox

def getctmtoken():
    """Get CTM auth token"""
    auth = HTTPBasicAuth(ctmUserId, ctmSecret)
    payload = {"grant_type": "client_credentials", "scope": ""}
    session = requests.Session()
    token_response = session.post(ctmEndpoint + ctmOauthBase, data=payload, auth=auth)
    token_json = json.loads(token_response.content)
    access_token = token_json.get("access_token")
    return access_token

def makecall(query, token):
    """Pull data from CTM"""
    headers = {'Authorization': 'Bearer ' + token}
    resp = requests.get(query, headers=headers)
    results = json.loads(resp.text)
    return results

def getrelatedname(obj):
    """Transform name field"""
    name = '(not available)'
    if len(obj) > 0:
        return obj[0]['name']
    return name

def getApplications(token):
    """Pull applications from CTM"""
    results = makecall(ctmEndpoint + ctmQueryBase + ctmAppQuery, token)
    applications = []
    for result in results['model']:
        application = {}
        application["name"] = result['name']
        application["description"] = result['description']
        application["id"] = result['_id']
        application["owningOrg"] = getrelatedname(result['owningOrganization'])
        application["itOwner"] = getrelatedname(result['ITOwner'])
        application["devOwner"] = getrelatedname(result['developmentOwner'])
        application["busOwner"] = getrelatedname(result['businessOwner'])
        application["recommendation"] = result['mmRecommendation']
        application["recommendationDate"] = result['recommendationDate']
        application["location"] = getrelatedname(result['isLocatedInLocation'])
        application["productionDate"] = result['productionDate']
        application["decommissionDate"] = result['decommissionDate']
        applications.append(application)
        #print(name + ' (' + id + ')')
    return applications

def getctmutilities(token):
    """Pull utilities from CTM"""
    results = makecall(ctmEndpoint + ctmQueryBase + ctmUtilQuery, token)
    utilities = []
    for result in results['model']:
        utility = {}
        utility["name"] = result['name']
        utility["description"] = result['description']
        utility["id"] = result['_id']
        utility["owningOrg"] = getrelatedname(result['hasOwningOrg'])
        utility["itOwner"] = getrelatedname(result['hasITOwnerUtil'])
        utility["devOwner"] = getrelatedname(result['hasDevelopmentOwner'])
        utility["busOwner"] = getrelatedname(result['utilHasBusinessOwner'])
        utility["recommendation"] = result['recommendation']
        utility["recommendationDate"] = result['recommendationDate']
        utility["location"] = getrelatedname(result['primaryHostingLocationUtil'])
        utilities.append(utility)
        #print(name + ' (' + id + ')')
    return utilities

def checkapp(app, vtarget, headers):
    """Check if an application exists in ZeroNorth"""
    url = 'https://api.zeronorth.io/v1/applications?expand=false&targetId={0}'.format(vtarget)
    resp = requests.get(url, headers=headers)
    apps = resp.json()
    if apps[1]["count"] > 0 :
        appid = apps[0][0]["id"]
    else:
        appid = None
    print(resp)
    return appid

def creatzneapplication(app, target, headers):
    """Create application in ZeroNorth"""
    appid = checkapp(app, target, headers)
    if appid is None:
        newappjson = {
            "name": app["name"],
            "targetIds": [target],
            "description": app["description"]
        }
        payload = json.dumps(newappjson)
        url = 'https://api.zeronorth.io/v1/applications'
        resp = requests.post(url, headers=headers, data=payload)
        print(resp)
        appid = resp.json()
    return appid

def checkvt(app, headers):
    """Check if a virtual target exists in ZeroNorth"""
    appname = app["name"].replace(" ", "%20")
    url = 'https://api.zeronorth.io/v1/targets?name={0}&virtual=true'.format(appname)
    resp = requests.get(url, headers=headers)
    apps = resp.json()
    for entry in apps[0]:
        if entry["data"]["environmentType"] == 'virtual-target' and entry["data"]["customerMetadata"]["id"] == app["id"]:
            targetid = entry["id"]
    print(resp)
    try:
        targetid
    except NameError:
        targetid = None
    return targetid

def createvirtualtarget(app, headers):
    """Create Virtual Target in ZeroNorth"""
    envid = "Bz47eFlHRPuuY3E7kgmCDQ" #dev
    targetid = checkvt(app, headers)
    if targetid is None:
        url = 'https://api.zeronorth.io/v1/targets'
        newtargetjson = {
            "name": app["name"],
            "environmentType": "virtual-target",
            "environmentId": envid,
            "integration": "application-placeholder",
            "parameters": {
                "name": app["name"]
                },
            "customerMetadata":{
                "id":app["id"],
                "owningOrg":app["owningOrg"],
                "itOwner":app["itOwner"],
                "devOwner":app["devOwner"],
                "busOwner":app["busOwner"],
                "recommendation":app["recommendation"],
                "recommendationDate":app["recommendationDate"],
                "location":app["location"],
                "productionDate":app["productionDate"],
                "decommissionDate":app["decommissionDate"]
                },
            "notifications": []
        }
        payload = json.dumps(newtargetjson)
        resp = requests.post(url, headers=headers, data=payload)
        targetid = resp.json()["id"]
    return targetid

def processctmtozn(apps,headers):
    """Process CTM applications to ZeroNorth applications"""
    for app in apps:
        virtualtarget = createvirtualtarget(app,headers)
        znapp = creatzneapplication(app, virtualtarget,headers)

def main():
    """main"""
    ctmtoken = getctmtoken()
    ctmapplications = getApplications(ctmtoken)
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {0}'.format(znSandbox)} #dev
    processctmtozn(ctmapplications,headers)
    #ctmutilities = getctmutilities(ctmtoken)
    print("done")

main()
