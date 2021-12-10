import json
import requests
import sys, os

#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import sqApi,sqUrl

url = "{0}api/components/search?qualifiers=TRK".format(sqUrl)

resp = requests.get(url, auth=(sqApi,''))
results = resp.json()
print(resp)
