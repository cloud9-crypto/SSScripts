
import sys
import os
import requests
import json
from requests.auth import HTTPBasicAuth

#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import ctmEndpoint, ctmUserId, ctmSecret, ctmOauthBase, ctmQueryBase, ctmAppQuery, ctmUtilQuery, znSandbox

def getToken():
    auth = HTTPBasicAuth(ctmUserId, ctmSecret)
    payload = {"grant_type": "client_credentials", "scope": ""}
    session = requests.Session()
    token_response = session.post(ctmEndpoint + ctmOauthBase, data=payload, auth=auth)
    token_json = json.loads(token_response.content)
    access_token = token_json.get("access_token")
    return access_token

def makeCall(query, token):
    apiHeader = {'Authorization': 'Bearer ' + token}
    apiCallResponse = requests.get(query, headers=apiHeader)
    results = json.loads(apiCallResponse.text)
    return results

def getRelatedName(obj):
    name = '(not available)'
    if len(obj) > 0:
        return obj[0]['name']
    return name

def getApplications(token):
    results = makeCall(ctmEndpoint + ctmQueryBase + ctmAppQuery, token)
    applications = []
    for result in results['model']:
        application = {}
        application["name"] = result['name']
        application["id"] = result['_id']
        application["owningOrg"] = getRelatedName(result['owningOrganization'])
        application["itOwner"] = getRelatedName(result['ITOwner'])
        application["devOwner"] = getRelatedName(result['developmentOwner'])
        application["busOwner"] = getRelatedName(result['businessOwner'])
        application["recommendation"] = result['mmRecommendation']
        application["recommendationDate"] = result['recommendationDate']
        application["location"] = getRelatedName(result['isLocatedInLocation'])
        application["productionDate"] = result['productionDate']
        application["decommissionDate"] = result['decommissionDate']
        applications.append(application)
        #print(name + ' (' + id + ')')
    return applications

def getUtilities(token):
    results = makeCall(ctmEndpoint + ctmQueryBase + ctmUtilQuery, token)
    utilities = []
    for result in results['model']:
        utility = {}
        utility["name"] = result['name']
        utility["id"] = result['_id']
        utility["owningOrg"] = getRelatedName(result['hasOwningOrg'])
        utility["itOwner"] = getRelatedName(result['hasITOwnerUtil'])
        utility["devOwner"] = getRelatedName(result['hasDevelopmentOwner'])
        utility["busOwner"] = getRelatedName(result['utilHasBusinessOwner'])
        utility["recommendation"] = result['recommendation']
        utility["recommendationDate"] = result['recommendationDate']
        utility["location"] = getRelatedName(result['primaryHostingLocationUtil'])
        utilities.append(utility)
        #print(name + ' (' + id + ')')
    return utilities

def main():
    token = getToken()
    ctmapplications = getApplications(token)
    print(ctmapplications)
    ctmutilities = getUtilities(token)

main()
