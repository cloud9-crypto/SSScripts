"""Creates a new application in ZeroNorth with the below details."""

import sys
import os
import json
import requests


#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import zn_api_key

def createapplication(app):
    ##NEED TO ADD VIRTUAL TARGET AS PLACEHOLDER
    
    """Create application in ZeroNorth"""
    payload = {
        "name": app["name"],
        "targetIds": [
            "string"
        ],
        "typeOfRiskEstimate": "none",
        "technicalImpact": {
            "confidentialityLoss": 0,
            "integrityLoss": 0,
            "availabilityLoss": 0,
            "accountabilityLoss": 0
        },
        "businessImpact": {
            "financialDamage": 0,
            "reputationDamage": 0,
            "nonCompliance": 0,
            "privacyViolation": 0
        },
        "description": "string"
    }
    url = 'https://api.zeronorth.io/v1/applications'
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {0}'.format(zn_api_key)}
    resp = requests.post(url, headers=headers, data=payload)
    print(resp)

def checkapplications(apps):
    """Compare data from CTM to what is currently in ZeroNorth to determine what applications need to be added"""
    znapps = getznapps()
    result = []
    for app in apps:
        if app["name"] in znapps["name"]:
            result.append(app)
    return result

def getznapps():
    """Get current list of apps from ZN"""
    url = 'https://api.zeronorth.io/v1/applications'
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {0}'.format(zn_api_key)}
    resp = requests.get(url, headers=headers)
    result = resp.json()
    return result


def getapplications():
    """Pull list of massmutual developed apps from CTM"""
    #pull from CTM API
    result = None
    print(result)
    return result

def main():
    """Main"""
    apps = getapplications()
    appstoadd = checkapplications(apps)
    for app in appstoadd:
        createapplication(app)

#start
main()
