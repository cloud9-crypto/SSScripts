
import sys
import os
import json
import requests
import time
import csv


#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import dtKey

def getapis():
    url = "https://apicatalog.db-api-prd.dsawsprd.massmutual.com/api/services"
    resp = requests.get(url)
    apis = resp.json()
    print(resp)
    return apis

def getspec(api):
    url = api["swaggerSpecLink"]
    if url != '':
        try:
            resp = requests.get(url)
            try:
                api['spec'] = resp.json()
                api['spec']['dataPowerProxyName'] = api['dataPowerProxyName']
            except:
                api['spec'] = "Error : {0}".format(str(resp))
                print(api["name"] + " - " + api["swaggerSpecLink"] + " | Resp: " + str(resp))
        except:
                api['spec'] = "Error : Connection"
                print(api["name"] + " - " + api["swaggerSpecLink"] + " | Resp: Connection Error")
    else:
        api['spec'] = "Error : Missing spec link"
        print(api["name"] + " - " + api["swaggerSpecLink"] + " | No API Spec link")
    try:
        if api['spec']['status'] is not None:
            api['spec'] = "Error : {0}".format(api['spec']['error'])
    
    except:
        api['spec'] = api['spec']
    return api

def uploadapispec(api):

    if isinstance(api['spec'], dict):
        url = "https://api.securetheorem.com/apis/api_security/results/v1beta1/openapi_definitions"
        headers = {'Authorization':'APIKey '+ dtKey,'Content-Type': 'application/json'}
        payload = api["spec"]
        payload = json.dumps(payload)
        resp = requests.post(url, headers=headers, data=payload)       #data.encode("utf-8"))
        #test = resp.json()
        print(resp)
    else:
        print("skipping due to swagger error")

def outputreport(apis):
    report = []
    for api in apis:
        entry = apientry(api)
        report.append(entry)
    csv_columns = list(report[0].keys())
    csv_columns.append('url')

    loc = "/Users/mm67226/OneDrive - MassMutual/Scripts/SoftwareSecurity/SSGScripts/APICatalog/apiexport.csv"
    try:
        with open(loc, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in report:
                writer.writerow(data)
    except IOError:
        print("I/O error")

def apientry(api):
    entry = {}
    entry['name'] = api['name']
    entry['createdAt'] = api['createdAt']
    entry['updatedAt'] = api['updatedAt']
    entry['dataPowerProxyName'] = api['dataPowerProxyName']
    entry['purpose'] = api['purpose']
    entry['swaggerSpecLink'] = api['swaggerSpecLink']
    entry['betaSwaggerSpecLink'] = api['betaSwaggerSpecLink']
    entry['docsLink'] = api['docsLink']
    #team
    try:
        entry['teamName'] = api['team']['name']
    except:
        entry['teamName'] = "Unknown"
    try:
        entry['emailDl'] = api['team']['mListEmailAddress']
    except:
        entry['emailDl'] = "Unknown"
    try:
        entry['Contact'] = api['team']['keyContactPerson']
    except:
        entry['Contact'] = "Unknown"
    #spec
    if isinstance(api['spec'], dict):
        try:
            #swagger
            entry['spec'] = "Swagger"
            entry['specVer'] = api['spec']['swagger']
            try:
                entry['host'] = api['spec']['host']
            except:
                entry['host'] = "Unknown"
            entry['basePath'] = api['spec']['basePath']
            
        except:
            #openapi
            entry['spec'] = "OpenAPI"
            entry['specVer'] = api['spec']['openapi']

            try:
                entry['url'] = api['spec']['servers'][0]['url']
            except:
                entry['url'] = "Unknown"
    else:
        entry['spec'] = api['spec']
    return entry

def main():
    apis = getapis()
    for api in apis:
        api = getspec(api)
    for api in apis:        
        if api is not None:
            #uploadapispec(api)
            print(None)
    outputreport(apis)
main()
