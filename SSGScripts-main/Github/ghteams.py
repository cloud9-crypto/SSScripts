import sys
import os
import requests
import csv

#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import githubtoken

def getteams():
    url = "https://api.github.com/orgs/massmutual/teams"
    resp = requests.get(url, headers=headers)
    results = resp.json()
    print(resp)

    return results

def getteamrepos(teams):
    for team in teams:
        url = "https://api.github.com/orgs/massmutual/teams/{0}/repos".format(team["slug"])
        resp = requests.get(url, headers=headers)
        results = resp.json()
        print(resp)

def main():
    teams = getteams()
    getteamrepos(teams)


auth = "token {0}".format(githubtoken)
headers = {'Content-Type': 'application/json', 'Authorization': auth, 'Accept': 'application/vnd.github.nebula-preview+json'}

main()