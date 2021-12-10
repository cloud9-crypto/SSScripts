import sys
import os
import requests
import csv
import yaml

#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import githubtoken,snykprodtoken,snykprodorg,snyktestingtoken,sntktestingorg

def getrepos():
    url = "https://api.github.com/orgs/massmutual/repos?type=all&per_page=100"
    auth = "token {0}".format(githubtoken)
    headers = {'Content-Type': 'application/json', 'Authorization': auth, 'Accept': 'application/vnd.github.nebula-preview+json'}
    report = []
    resp = requests.get(url, headers=headers)
    results = resp.json()
    for result in results:
        if "ssg" in result["name"] or "SSG" in result["name"]:
            report.append(result)
    count = str(len(report))
    print("Results so far : " + count)
    cpage = int(resp.links["next"]["url"].split("&page=",1)[1])
    lpage = int(resp.links["last"]["url"].split("&page=",1)[1])

    while cpage < lpage:
        lpage = int(resp.links["last"]["url"].split("&page=",1)[1])
        cpage = int(resp.links["next"]["url"].split("&page=",1)[1])
        print("Processing page " + str(cpage) + " of " + str(lpage))
        resp = requests.get(resp.links["next"]["url"], headers=headers)
        results = resp.json()
        for result in results:
            if "ssg" in result["name"] or "SSG" in result["name"]:
                report.append(result)
        count = str(len(report))
        print("Results so far : " + count)
    return report

def exporttoexcel(array,csv_file):
    """export data to csv"""
    csv_columns = list(array[0].keys())
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in array:
                writer.writerow(data)
    except IOError:
        print("I/O error")

def pullsnyk():

    url = 'https://snyk.io/api/v1/org/{0}/projects'.format(sntktestingorg)
    auth = "token {0}".format(snyktestingtoken)
    headers = {"Authorization": auth, "Content-Type":"application/json; charset=utf-8"}

    resp = requests.post(url, headers=headers)
    results = resp.json()["projects"]
    print(resp)
    for result in results:
        result["group"] = "Unknown"
        result["org"] = "Unknown"
        if result["tags"] != []:
            for tag in result["tags"]:
                if tag["key"] == "group":
                    result["group"] = tag["value"]
                elif tag["key"] == "org":
                    result["org"] = tag["value"]
        
        result["low"] = result["issueCountsBySeverity"]["low"]
        result["medium"] = result["issueCountsBySeverity"]["medium"]
        result["high"] = result["issueCountsBySeverity"]["high"]
        result["critical"] = result["issueCountsBySeverity"]["critical"]
        result.pop('importinguser', None)
        result.pop('tags', None)
        result.pop('attributes', None)
        result.pop('imageTag', None)
        result.pop('imageBaseImage', None)
        result.pop('imageId', None)
        result.pop('imagePlatform', None)
        result.pop('issueCountsBySeverity', None)

    return results

def initrepo(item):
    repo = {}
    repo["sastlow"] = 0
    repo["sastmedium"] = 0
    repo["sasthigh"] = 0
    repo["sastcritical"] = 0
    repo["scalow"] = 0
    repo["scamedium"] = 0
    repo["scahigh"] = 0
    repo["scacritical"] = 0
    repo["imagelow"] = 0
    repo["imagemedium"] = 0
    repo["imagehigh"] = 0
    repo["imagecritical"] = 0
    repo["iaclow"] = 0
    repo["iacmedium"] = 0
    repo["iachigh"] = 0
    repo["iaccritical"] = 0
    repo["name"] = item["full_name"]
    repo["count_forks"] = item["forks"]
    if repo["count_forks"] > 3:
        repo["forking"] = True
    else:
        repo["forking"] = False
    repo["visibility"] = item["visibility"]
    repo["disabled"] = item["disabled"]
    repo["archived"] = item["archived"]
    repo["language"] = item["language"]
    repo["default_branch"] = item["default_branch"]
    repo["description"] = item["description"]
    repo["created_at"] = item["created_at"]
    repo["pushed_at"] = item["pushed_at"]
    repo["SAST"] = False
    repo["SCA"] = False
    repo["IaC"] = False
    repo["Image"] = False

    return(repo)

def processsnyk(repo,snyksast,snykimage,snykiac,snyksca):
        #check SAST
        for entry in snyksast:
            if repo["name"] == entry["name"]:
                repo["SAST"] = True
                repo["sastlow"] = repo["sastlow"] + entry["low"]
                repo["sastmedium"] = repo["sastmedium"] + entry["medium"]
                repo["sasthigh"] = repo["sasthigh"] + entry["high"]
                repo["sastcritical"] = repo["sastcritical"] + entry["critical"]

        #check Image
        for entry in snykimage:
            if repo["name"] == (entry["name"].split(":"))[0]:
                repo["Image"] = True
                repo["imagelow"] = repo["imagelow"] + entry["low"]
                repo["imagemedium"] = repo["imagemedium"] + entry["medium"]
                repo["imagehigh"] = repo["imagehigh"] + entry["high"]
                repo["imagecritical"] = repo["imagecritical"] + entry["critical"]
        
        #check IaC
        for entry in snykiac:
            if repo["name"] == (entry["name"].split(":"))[0]:
                repo["IaC"] = True
                repo["iaclow"] = repo["iaclow"] + entry["low"]
                repo["iacmedium"] = repo["iacmedium"] + entry["medium"]
                repo["iachigh"] = repo["iachigh"] + entry["high"]
                repo["iaccritical"] = repo["iaccritical"] + entry["critical"]

        #check SCA
        for entry in snyksca:
            if repo["name"] == (entry["name"].split(":"))[0]:
                repo["SCA"] = True
                repo["scalow"] = repo["scalow"] + entry["low"]
                repo["scamedium"] = repo["scamedium"] + entry["medium"]
                repo["scahigh"] = repo["scahigh"] + entry["high"]
                repo["scacritical"] = repo["scacritical"] + entry["critical"]
        
        #Does repo have scannable content?
        if repo["SCA"] == True or repo["SAST"] == True or repo["IaC"] == True or repo["Image"] == True:
            repo["scannable"] = True
        else:
            repo["scannable"] = False
        
        #Does repo have critical or high issues?
        if repo["scacritical"] == 0 and repo["scahigh"] == 0 and repo["sasthigh"] == 0 and repo["sastcritical"] == 0 and repo["imagehigh"] == 0 and repo["imagecritical"] == 0 and repo["iachigh"] == 0 and repo["iaccritical"] == 0:
            repo["criticalorhigh"] = False
        else:
            repo["criticalorhigh"] = True
        
        #Get metadata
        meta = getmetadata(repo)
        repo["group"] = meta["group"]
        repo["org"] = meta["org"]


        return(repo)

def getmetadata(repo):
    meta = {}
    url = "https://api.github.com/repos/{0}/contents/snyk.yaml".format(repo["name"])
    try:
        resp = requests.get(url, headers=headers)
        results = resp.json()
        dlurl = results["download_url"]
        resp2 = requests.get(dlurl, headers=headers)
        meta = yaml.safe_load(resp2.text)
    except:
        meta["group"] = "Unknown"
        meta["org"] = "Unknown"
    
    return meta

def combine(snyk,github):
    snyksast = []
    snyksca = []
    snykiac = []
    snykimage = []
    report = []
    
    #Process Snyk to files by scan type
    for entry in snyk:
        if entry['type'] == "sast":
            snyksast.append(entry)
        elif entry['type'] == "dockerfile":
            snykimage.append(entry)
        elif entry['type'] == "terraformconfig" or entry['type'] == "cloudformationconfig" or entry['type'] == "helmconfig" or entry['type'] == "k8sconfig" or entry['type'] == "helmconfig":
            snykiac.append(entry)
        elif entry['type'] == "pip" or entry['type'] == "npm" or entry['type'] == "maven" or entry['type'] == "nuget" or entry['type'] == "gradle" or entry['type'] == "gomodules" or entry['type'] == "yarn":
            snyksca.append(entry)
        elif entry['type'] == "sbt" or entry['type'] == "rubygems" or entry['type'] == "cocoapods" or entry['type'] == "composer" or entry['type'] == "golangdep" or entry['type'] == "govendor":
            snyksca.append(entry)
        else:
            error = "TYPE NOT FOUND : " + entry["type"]
            print(error)

    count = 0
    count2 = 0
    total = len(github)
    print("Processing repos")
    print(("Processed {0} of {1}").format(count,total))
    for item in github:
        count = count + 1
        count2 = count2 + 1
        if count2 > 99:
            print(("Processed {0} of {1}").format(count,total))
            count2 = 0
        repo = initrepo(item)
        repo = processsnyk(repo,snyksast,snykimage,snykiac,snyksca)
        report.append(repo)
    
    return report

def main():
    #pull repos from Github
    ghreport = getrepos()

    #pull Snyk results
    snykreport = pullsnyk()

    #snyk export
    #snykexport = "/Users/mm67226/OneDrive - MassMutual/Scripts/SoftwareSecurity/SSGScripts/Snyk/snyk2.csv"
    #exporttoexcel(snykreport,snykexport)
    
    #GH export
    #ghexport = "/Users/mm67226/OneDrive - MassMutual/Scripts/SoftwareSecurity/SSGScripts/Snyk/repos2.csv"
    #exporttoexcel(ghreport,ghexport)

    #Combine Snyk and GitHub
    report = combine(snykreport,ghreport)

    #Combined export
    reportexport = "/Users/mm67226/OneDrive - MassMutual/Scripts/SoftwareSecurity/SSGScripts/Snyk/importreport.csv"
    exporttoexcel(report,reportexport)

    print("Done")

main()
