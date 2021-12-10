"""Checks for abandoned policies"""

import os
import sys
import json
import requests
import xlwt

#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import zn_api_key

def getznpolicies():
    """Get all policies from ZN"""
    policies = []
    url = 'https://api.zeronorth.io/v1/policies?limit=999999'
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {0}'.format(zn_api_key)}
    resp = requests.get(url, headers=headers)
    policies = resp.json()[0]
    print(resp)
    return policies

def parsepolicies(policies, scenarios):
    """Parse policy data"""
    parsed = {}
    for scenario in scenarios:
        parsed[scenario] = []
    for policy in policies:
        temp = policy["data"]["scenarios"][0]["name"]
        parsed[temp].append(policy)
    return parsed

def getscenarios():
    """Get list of current scenarios"""
    url = 'https://api.zeronorth.io/v1/scenarios?expand=false'
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {0}'.format(zn_api_key)}
    resp = requests.get(url, headers=headers)
    results = resp.json()
    print(resp)
    scenarios = []
    for result in results[0]:
        scenarios.append(result["data"]["name"])
    return scenarios

def outputpolicies(policies):
    """Write policies to file"""
    exportxls = xlwt.Workbook(encoding="utf-8")
    sheets = {}
    for scenario in policies:
        if "smells" not in scenario:
            array = policies[scenario]
            sheets[scenario] = exportxls.add_sheet(scenario,cell_overwrite_ok=True)
            sheets[scenario].write(0, 0, 'Policy ID')
            sheets[scenario].write(0, 1, 'Name')
            sheets[scenario].write(0, 2, 'Created At')
            sheets[scenario].write(0, 3, 'Last Run')
            row = 1
            for policy in array:
                sheets[scenario].write(row, 0, policy["id"])
                sheets[scenario].write(row, 1, policy["data"]["name"])
                sheets[scenario].write(row, 2, policy["meta"]["created"])
                sheets[scenario].write(row, 3, policy["lastrun"])
                row = row + 1
    exportxls.save("/users/mm67226/policiesexport.xls")

def getpolicyrun(policies, scenarios):
    """Get last time policy finished"""
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {0}'.format(zn_api_key)}
    url = 'https://api.zeronorth.io/v1/reports/policyRunStatistics?groupByPolicy=false&limit=1&offset=0&status=FINISHED'
    znresults = []
    for scenario in scenarios:
        data = []
        for entry in policies[scenario]:
            data.append(entry["id"])
        payload = {}
        payload["policyIds"] = data
        payload = json.dumps(payload)
        resp = requests.post(url, headers=headers, data=payload)
        znresults.append(resp.json())
        processedresults = []
        for result in znresults:
            for record in result:
                processedresults.append(record)
        print(resp)
    for scenario in scenarios:
        for entry in policies[scenario]:
            policyid = entry["id"]
            entry["lastrun"] = "unknown"
            for result in processedresults:
                if result["policyId"] == policyid:
                    entry["lastrun"] = result["events"][0]["meta"]["created"]
                    break
    return policies

def main():
    """main"""
    #start
    policies = getznpolicies()
    scenarios = getscenarios()
    parsedpolicies = parsepolicies(policies,scenarios)
    policyresults = getpolicyrun(parsedpolicies,scenarios)
    outputpolicies(policyresults)

#start
main()
