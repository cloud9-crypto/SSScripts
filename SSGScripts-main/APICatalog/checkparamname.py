
import sys
import os
import json
import requests
import time
import csv

def getapis():
    url = "https://apicatalog.db-api-prd.dsawsprd.massmutual.com/api/services"
    resp = requests.get(url)
    apis = resp.json()
    print(resp)
    return apis

def getspec(api):
    
    url = api["swaggerSpecLink"]
    if url == '':
        url = api["betaSwaggerSpecLink"]
    if url != '':
        try:
            resp = requests.get(url)
            try:
                api['spec'] = resp.json()
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
    api = apidetails(api)
    return api

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

def apidetails(api):
    #spec
    if isinstance(api['spec'], dict):
        try:
            #swagger
            api['specType'] = "Swagger"
            api['specVer'] = api['spec']['swagger']
        except:
            #openapi
            api['specType'] = "OpenAPI"
            api['specVer'] = api['spec']['openapi']
    else:
        api['specType'] = ""
        api['specVer'] = ""
    return api

def checkspec(apis):
    params = []
    for api in apis:
        if api['specType'] != '':
            pathlist = list(api['spec']['paths'].keys())
            for path in pathlist:
                methodlist = list(api['spec']['paths'][path].keys())
                for method in methodlist:
                    try:
                        for param in api['spec']['paths'][path][method]['parameters']:
                            params.append(param['name'])
                    except:
                        time.sleep(0)
    return params


def main():
    apis = getapis()
    
    for api in apis:
        api = getspec(api)

    report = checkspec(apis)
    print(len(report))
    for entry in report:
        print(entry)

    #outputreport(apis)

main()
