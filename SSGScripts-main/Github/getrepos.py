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
    url = "https://api.github.com/orgs/massmutual/repos?type=all&per_page=100"

    resp = requests.get(url, headers=headers)
    results = resp.json()
    processresults(results)
    cpage = int(resp.links["next"]["url"].split("&page=",1)[1])
    lpage = int(resp.links["last"]["url"].split("&page=",1)[1])

    while cpage < lpage:
        lpage = int(resp.links["last"]["url"].split("&page=",1)[1])
        cpage = int(resp.links["next"]["url"].split("&page=",1)[1])
        print("Processing page " + str(cpage) + " of " + str(lpage))
        resp = requests.get(resp.links["next"]["url"], headers=headers)
        results = resp.json()
        processresults(results)

def processresults(results):
    for result in results:
        report.append(result)
    count = str(len(report))
    print("Results so far : " + count)

def exporttoexcel(array):
    """export data to csv"""
    csv_columns = list(array[0].keys())
    csv_file = "/Users/mm67226/OneDrive - MassMutual/Scripts/SoftwareSecurity/SSGScripts/Github/repos.csv"
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

report=[]
auth = "token {0}".format(githubtoken)
headers = {'Content-Type': 'application/json', 'Authorization': auth, 'Accept': 'application/vnd.github.nebula-preview+json'}
main()
