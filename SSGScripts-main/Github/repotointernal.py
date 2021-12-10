import sys
import os
import requests
import csv

#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import githubtoken

def getrepos():
    #url = "https://api.github.com/orgs/massmutual/repos?type=all&per_page=100"
    url = "https://api.github.com/orgs/massmutual/repos?type=all&per_page=10"

    resp = requests.get(url, headers=headers)
    results = resp.json()
    processresults(results)
    #cpage = int(resp.links["next"]["url"].split("&page=",1)[1])
    #lpage = int(resp.links["last"]["url"].split("&page=",1)[1])

    #while cpage < lpage:
    #    lpage = int(resp.links["last"]["url"].split("&page=",1)[1])
    #    cpage = int(resp.links["next"]["url"].split("&page=",1)[1])
    #    print("Processing page " + str(cpage) + " of " + str(lpage))
    #    resp = requests.get(resp.links["next"]["url"], headers=headers)
    #    results = resp.json()
    #    processresults(results)

def processresults(results):
    for result in results:
        report.append(result)
    count = str(len(report))
    print("Results so far : " + count)

def exporttoexcel(array):
    """export data to csv"""
    csv_columns = list(array[0].keys())
    csv_file = "/Users/mm67226/OneDrive - MassMutual/Scripts/SoftwareSecurity/SSGScripts/Github/repos2.csv"
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in array:
                writer.writerow(data)
    except IOError:
        print("I/O error")

def main():
    getrepos()
    exporttoexcel(report)
    findprivate(report)

def makeinternal(reponame):
    url = "https://api.github.com/repos/{0}".format(reponame)
    body = {'visibility': 'internal'}
    #resp = requests.patch(url, headers=headers,json=body)
    results = resp.json()
    print(resp)

def findprivate(repos):
    pcount = 0
    print(len(repos))
    for repo in repos:
        if repo["visibility"] == "private":
            pcount = pcount + 1
            print(repo["full_name"])
            #makeinternal(repo["full_name"])
    print(pcount)


report=[]
auth = "token {0}".format(githubtoken)
headers = {'Content-Type': 'application/json', 'Authorization': auth, 'Accept': 'application/vnd.github.nebula-preview+json'}
main()
