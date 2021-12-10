"""Get DAST scan results from Qualys"""

import json
import sys
import os
import xml.etree.ElementTree as xml
import requests

#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import qualysUser, qualysPass, qualysUrl, ptUser, ptPass, ptClientId, ptUrl

def getplextoken():
    """Gets JWT from Plextrac"""
    url = "{0}/api/v1/authenticate".format(ptUrl)
    payload = {'username': ptUser, 'password': ptPass}
    payload_json = json.dumps(payload)
    authheaders = {'Content-Type': 'application/json'}
    resp = requests.request("POST", url, headers=authheaders, data=payload_json)
    print(resp)
    return resp.json()["token"]

def getqualyswebapps():
    """Gets list of Web Apps from Qualys"""
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "user": qualysUser,
        "password": qualysPass
    }
    url = '{0}/qps/rest/3.0/search/was/webapp'.format(qualysUrl)
    resp = requests.post(url, headers=(headers))
    results = resp.json()
    print(resp)
    return results

def processwebapps(webapps,plextoken):
    """Processes Qualys Web Apps to Plextrac Reports"""
    for webapp in webapps["ServiceResponse"]["data"]:
        reportid = createqualysreport(webapp["WebApp"])
        qualysreport = getqualysreport(reportid)
        qualystoplextrac(qualysreport,plextoken)

def qualystoplextrac(report,plextoken):
    """Creates reports in Plextrac then upload Qualys XML"""
    plexreportid = createplexreport(report,plextoken)
    url = "{0}/client/{1}/report/{2}/import/qualys".format(ptUrl, ptClientId, plexreportid)
    headers = {'Authorization': '{0}'.format(plextoken)}
    payload = {}
    files = [
      ('file', open('qualysreport.xml','rb'))
    ]
    resp = requests.request("POST", url, headers=headers, data = payload, files = files)
    result = resp.json()
    print(resp.text.encode('utf8'))

def getqualysreport(reportid):
    """Gets Qualys XML report and saves it locally"""
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "user": qualysUser,
        "password": qualysPass
    }
    url = '{0}/qps/rest/3.0/download/was/report/{1}'.format(qualysUrl, reportid)
    resp = requests.get(url, headers=(headers))
    tree = stringtoxml(resp.content)
    print(resp)
    export = xml.ElementTree()
    export._setroot(tree)
    export.write("/users/mm67226/qualysreport.xml") # TEMP FIX LATER
    return tree

def createplexreport(report,plextoken):
    """Create new report in Plextrac"""
    for entry in report.iter('NAME'): #FIX LATER
        name = entry.text
        break
    url = "{0}/api/v1/client/{1}/report/create".format(ptUrl, ptClientId)
    fieldtemplateid = "9fa701cb-4478-424a-9494-428afec4143e"
    payload = {'name': name, 'fields_template':fieldtemplateid}
    headers = {'Authorization': '{0}'.format(plextoken)}
    resp = requests.request("POST", url, headers=headers, data = payload)
    reportid = resp.json()["report_id"]
    print(resp)
    return reportid

def createqualysreport(webapp):
    """Create Qualys Web App Report"""
    url = "{0}/qps/rest/3.0/create/was/report".format(qualysUrl)
    headers = {
        "user": qualysUser,
        "password": qualysPass,
        "content-type": "text/xml"
    }
    #create XML
    payload = createxml(webapp)
    #Create report
    resp = requests.post(url, headers=headers, data=payload)
    #Parse ID from response
    tree = stringtoxml(resp.content)
    for entry in tree.iter('id'):
        reportid = entry.text
    print(resp)
    return reportid

def stringtoxml(string):
    """Convert string to XML"""
    string_xml = string
    xmltree = xml.fromstring(string_xml)
    return xmltree

def createxml(webapp):
    """Construct XML for Qualys report creation"""
    #create XML
    ServiceRequest = xml.Element("ServiceRequest")
    data = xml.SubElement(ServiceRequest, 'data')
    Report = xml.SubElement(data, 'Report')
    name = xml.SubElement(Report, 'name')
    name.text = webapp["name"]
    format1 = xml.SubElement(Report, 'format')
    format1.text = "XML"
    type1 = xml.SubElement(Report, 'type')
    type1.text = "WAS_WEBAPP_REPORT"
    config = xml.SubElement(Report, 'config')
    webAppReport = xml.SubElement(config, 'webAppReport')
    target = xml.SubElement(webAppReport, 'target')
    webapps = xml.SubElement(target, 'webapps')
    WebApp1 = xml.SubElement(webapps, 'WebApp')
    id1 = xml.SubElement(WebApp1, 'id')
    id1.text = str(webapp["id"])
    payload = xml.tostring(ServiceRequest)
    return payload

def getqualys():
    """Get reports from Qualys"""
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "user": qualysUser,
        "password": qualysPass
    }
    url = "{0}/qps/rest/3.0/search/was/report".format(qualysUrl)
    resp = requests.post(url, headers=(headers))
    reports = resp.json()["ServiceResponse"]["data"]
    print(resp)
    return reports

def processreports(reports):
    """Create new report in Plextrac"""
    for report in reports:
      plexReportId = createreport(report)
      
      
      url = '{0}/qps/rest/3.0/download/was/report/{1}'.format(qualysUrl, report["Report"]["id"])
      resp = requests.get(url, headers=(headers))
      result = resp.text
      print(resp)

def addfindings():
    """Create report from Qualys report"""
    url = "{0}/client/{1}/report/{2}/import/qualys".format(ptUrl,ptClientId,reportId)

    payload = {}
    files = [
      ('file', open('/path/to/file','rb'))
    ]
    headers= {}

    response = requests.request("POST", url, headers=headers, data = payload, files = files)

    print(response.text.encode('utf8'))

def main():
    """Main"""
    #get plex token
    plextoken = getplextoken()
    #get qualys web apps
    qualyswebapps = getqualyswebapps()
    #process web apps
    processwebapps(qualyswebapps,plextoken)
    #get qualys reports
    qualysreports = getqualys()
    #Process reports
    processreports(qualysreports)
    #findings
    #addfindings()

#start
main()
