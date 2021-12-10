#Updates ZeroNorth targets based on xlsx input
"""Updates ZeroNorth targets based on xlsx input"""

import os
import sys
import json
import requests
import xlrd

#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import zn_api_key

#define variables
token = zn_api_key
headers = {'Content-Type': 'application/json','Authorization': 'Bearer {0}'.format(token)}

#Input file
loc = "{0}/ZN_Target_cleanup.xls".format(currentdir)
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)

#init list
components = []

#process workday data into list
for row in range(0, sheet.nrows):
    if row > 0:
        components.append({
            'znid': sheet.cell_value(row, 0),
            'name': sheet.cell_value(row, 1),
            'bu': sheet.cell_value(row, 2),
            'pipeline': sheet.cell_value(row, 3),
            'team': sheet.cell_value(row, 4)})

print(len(components))

for component in components:
    #pull data
    url = 'https://api.zeronorth.io/v1/targets/{0}'.format(component["znid"])
    resp = requests.get(url, headers=headers)
    print(resp)

    #load data
    target = resp.json()["data"]
    target["customerMetadata"] = {"BU": component["bu"],"Pipeline": component["pipeline"],"Team": component["team"]}
    target["tags"] = [component["bu"], component["pipeline"], component["team"]]
    del target["excludeRegex"]
    del target["includeRegex"]
    del target["notifications"]
    del target["virtualTargets"]
    del target["physicalTargets"]

    #print and put changes
    print(target["name"],component["bu"],component["pipeline"],component["team"])
    payload = json.dumps(target)
    resp2 = requests.put(url, headers=headers, data=payload)
    print(resp2)
