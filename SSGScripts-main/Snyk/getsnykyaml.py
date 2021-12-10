import sys
import os
import requests
import csv
import yaml

#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import githubtoken,snykprodtoken,snykprodorg

#https://api.github.com/repos/massmutual/ssg-test/contents/snyk.yaml
#https://github.com/massmutual/ssg-test/blob/main/snyk.yaml

#url = "https://api.github.com/orgs/massmutual/repos/ssg-test/contents/snyk.yaml"
url = "https://api.github.com/repos/massmutual/ssg-test/contents/snyk.yaml"
auth = "token {0}".format(githubtoken)
headers = {'Content-Type': 'application/json', 'Authorization': auth, 'Accept': 'application/vnd.github.nebula-preview+json'}
resp = requests.get(url, headers=headers)
results = resp.json()
dlurl = results["download_url"]
resp2 = requests.get(dlurl, headers=headers)
results2 = yaml.safe_load(resp2.text)
print(resp2)






