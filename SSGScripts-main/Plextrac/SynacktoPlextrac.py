"""Pull results from Synack and upload to Plextrac"""

import json
import sys
import os
import requests

#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import synToken, ptUser, ptPass, ptClientId, ptUrl, synUrl

def getplextoken():
    """Gets JWT from Plextrac"""
    url = "{0}/api/v1/authenticate".format(ptUrl)
    payload = {'username': ptUser, 'password': ptPass}
    payload_json = json.dumps(payload)
    authheaders = {'Content-Type': 'application/json'}
    resp = requests.request("POST", url, headers=authheaders, data=payload_json)
    print(resp)
    return resp.json()["token"]

def getassessments():
    """Get list of assessments in Synack"""
    url = "{0}/v1/assessments".format(synUrl)
    headers = {'Authorization': 'Bearer {0}'.format(synToken)}
    resp = requests.get(url, headers=headers)
    print(resp)
    results = resp.json()
    return results

def getplexreports(plextoken):
    """Get list of reports in Plextrac"""
    ssgreports = []
    url = "{0}/api/v1/reports".format(ptUrl)
    headers = {'Authorization': '{0}'.format(plextoken)}
    resp = requests.request("GET", url, headers=headers)
    results = resp.json()
    for entry in results:
        if entry["doc_id"] == [3531]:
            ssgreports.append(entry)
    return ssgreports

def assignmentstoreports(assessments, reports, plextoken):
    """Process assessments into Plextrac reports"""
    reportlist = []
    for report in reports: # this is bad and I should feel bad.  FIX LATER
        temp = report["data"]
        reportlist.append(temp[1])
    for assessment in assessments:
        if assessment["codename"] not in reportlist:
            createreport(assessment["codename"],assessment["description"],assessment["details"],plextoken)

def createreport(name, description, logistics,plextoken):
    """Create new report in Plextrac"""
    url = "{0}/api/v1/client/{1}/report/create".format(ptUrl, ptClientId)
    fieldtemplateid = "9fa701cb-4478-424a-9494-428afec4143e"
    payload = {'name': name, 'description': description, 'logistics': logistics, 'fields_template':fieldtemplateid}
    headers = {'Authorization': '{0}'.format(plextoken)}
    resp = requests.request("POST", url, headers=headers, data = payload)
    print(resp.text.encode('utf8'))

def reportmapping(assessments, reports):
    """Maps Plextrac reports to Synack assessments"""
    mapping = {'key': 'value'}
    for assessment in assessments:
        for report in reports:
            if report["data"][1] == assessment["codename"]:
                mapping[assessment["codename"]] = report["data"][0]
    return mapping

def parsefindings(assessments, reportmap, plextoken):
    """Parses findings for ones to add"""
    url = "{0}/v1/vulnerabilities".format(synUrl)
    headers = {'Authorization': 'Bearer {0}'.format(synToken)}
    for assessment in assessments:
        report = reportmap[assessment["codename"]]
        params = { "filter[search]": "{0}".format(assessment["codename"])}
        resp = requests.get(url, headers=headers, params=params)
        results = resp.json()
        print(resp)
        for result in results:
            addfinding(report, result, plextoken)

def getcvsscalc(cvssblob,blob):
    """Parses CVSS questions"""
    for entry in blob:
        if entry["question"] == "Is this an attack over network or local?":
            #Network
            if entry["response"] == "Network":
                cvssblob = cvssblob + "AV:N/"
            elif entry["response"] == "Adjacent Network":
                cvssblob = cvssblob + "AV:A/"
            elif entry["response"] == "Local":
                cvssblob = cvssblob + "AV:L/"
            elif entry["response"] == "Physical":
                cvssblob = cvssblob + "AV:P/"
        elif entry["question"] == "What is the complexity of executing this vulnerability?":
            #Complexity
            if entry["response"] == "Low":
                cvssblob = cvssblob + "AC:L/"
            elif entry["response"] == "High":
                cvssblob = cvssblob + "AC:H/"
        elif entry["question"] == "What level of privileges is required to execute this vulnerability?":
        #Privilege
            if entry["response"] == "None":
                cvssblob = cvssblob + "PR:N/"   
            elif entry["response"] == "Basic":
                cvssblob = cvssblob + "PR:L/"   
            elif entry["response"] == "Admin":
                cvssblob = cvssblob + "PR:H/"   
        elif entry["question"] == "Is any interaction from another user required to execute this vulnerability?":
            #user interaction
            if entry["response"] == "None":
                cvssblob = cvssblob + "UI:N/"
            if entry["response"] == "Required":
                cvssblob = cvssblob + "UI:R/"
        elif entry["question"] == "Does the exploit affect resources or systems outside the scope of this vulnerability?":
            #scope
            if entry["response"] == "Yes":
                cvssblob = cvssblob + "S:C/"
            if entry["response"] == "No":
                cvssblob = cvssblob + "S:U/"
        elif entry["question"] == "Does this vulnerability impact confidentiality?":
            #C
            if entry["response"] == "None":
                cvssblob = cvssblob + "C:N/"
            elif entry["response"] == "Low Impact":
                cvssblob = cvssblob + "C:L/"
            elif entry["response"] == "High Impact":
                cvssblob = cvssblob + "C:H/"
        elif entry["question"] == "Is the integrity of the application or user data compromised?":
            #I
            if entry["response"] == "None":
                cvssblob = cvssblob + "I:N/"
            elif entry["response"] == "Yes, for a single user":
                cvssblob = cvssblob + "I:L/"
            elif entry["response"] == "Yes, for more than one user":
                cvssblob = cvssblob + "I:H/"
        elif entry["question"] == "Could this vulnerability have any impact on application availability?":
            #A
            if entry["response"] == "None":
                cvssblob = cvssblob + "A:N"
            elif entry["response"] == "Yes, for a single user":
                cvssblob = cvssblob + "A:L"
            elif entry["response"] == "Yes, for more than one user":
                cvssblob = cvssblob + "A:H"
    return cvssblob

def addfinding(reportid, result, plextoken):
    """Create new finding in Plextrac"""
    #parse exploitable_locations
    locations = ""
    assets=[]
    for entry in result["exploitable_locations"]:
        assets.append(entry["value"])
        locations = locations + "\n" + entry["type"] + " : " + entry["value"]
    #cvss blob - Not the best but not sure of a better way to parse
    cvsslabel = "CVSS" + result["cvss_version"]
    cvssblob = cvsslabel + "/"
    cvsscalc = getcvsscalc(cvssblob, result["cvss_blob"])
    #fields
    fields = {
        'cve_idis': {
            'label': 'cve_ids',
            'value': result["cve_ids"]
        },
        'cwe_ids': {
            'label': 'cwe_ids',
            'value': result["cwe_ids"]
        },
        "scores": {
            "cvss3": {
                "label": cvsslabel,
                "value": result["cvss_final"],
                "calculation": cvsscalc
            }
        }
    }
    #severity logic
    if result["cvss_final"] <= 1.0:
        severity = "Informational"
    elif result["cvss_final"] > 1.0 and result["cvss_final"] <= 2.5:
        severity = "Low"
    elif result["cvss_final"] > 2.5 and result["cvss_final"] <= 5.0:
        severity = "Medium"
    elif result["cvss_final"] > 5.0 and result["cvss_final"] <= 7.5:
        severity = "High"
    elif result["cvss_final"] > 7.5:
        severity = "Critical"
    #link to Synack
    linkhtml = '<a href="' + result["link"] + '" target="_blank">' + result["id"] + "</a>"
    link = "\n" + "<h3><b>Synack link</b></h3>" + "\n" + linkhtml + "\n<br>"
    #impact
    impact = "\n" + "<h3><b>Impact</b></h3>" + "\n" + result["impact"] + "\n<br>"
    #validation steps
    #why are these not in order???
    steps = []
    stepnum = 0
    num = len(result["validation_steps"])
    while stepnum != num:
        stepnum = stepnum + 1
        for step in result["validation_steps"]:
            if step["number"] == stepnum:
                steps.append(step)
    validation = "\n" + "<h3><b>Validation Steps</b></h3>" + "\n"
    for step in steps:
        validation = validation + str(step["number"]) + " : " + step["detail"] + "<br>\n"
    #references
    references = link + impact + validation
    #payload
    url = "{0}/api/v1/client/{1}/report/{2}/flaw/create".format(ptUrl, ptClientId, reportid)
    payload = {
        'id': result["id"],
        'title': result["title"],
        'description': result["description"],
        'severity': severity,
        'references': references,
        'recommendations': result["recommended_fix"],
        #'affected_assets': assets,
        'assignedTo': 'BSantiago@massmutual.com',
        'status': 'Open',
        'source': 'Synack',
        'fields': fields
        }
    files = []
    headers = {'Authorization': plextoken}
    resp = requests.request("POST", url, headers=headers, json=payload, files=files)
    print(resp)

def main():
    """Main"""
    #Get Plextrac auth token
    plextoken = getplextoken()
    #Get list of assessments from Synack
    synassessments = getassessments()
    #Get list of reports from Plextrac
    plexreports = getplexreports(plextoken)
    #process assessments into reports if not already present
    assignmentstoreports(synassessments, plexreports,plextoken)
    #Update reports
    plexreports = getplexreports(plextoken)
    #Create report mapping
    reportmap = reportmapping(synassessments, plexreports)
    #Create findings from assessment vulns
    parsefindings(synassessments, reportmap, plextoken)
    #print(synassessments, plexreports)

#start
main()
