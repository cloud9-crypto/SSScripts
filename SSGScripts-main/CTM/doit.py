import requests, json
from requests.auth import HTTPBasicAuth
import config as cfg


def getToken():
    auth = HTTPBasicAuth(cfg.USERID, cfg.SECRET)
    payload = {"grant_type": "client_credentials", "scope": ""}
    session = requests.Session()
    token_response = session.post(cfg.ENDPOINT + cfg.OAUTHBASE, data=payload, auth=auth)
    token_json = json.loads(token_response.content)
    access_token = token_json.get("access_token")
    return access_token


def makeCall(query, token):
    apiHeader = {'Authorization': 'Bearer ' + token}
    apiCallResponse = requests.get(query, headers=apiHeader)
    results = json.loads(apiCallResponse.text)
    return results


def getRelatedName(obj):
    name = '(not available)'
    if len(obj) > 0:
        return obj[0]['name']
    return name


def getApplications(token):
    results = makeCall(cfg.ENDPOINT + cfg.QUERYBASE + cfg.APPQUERY, token)
    for result in results['model']:
        name = result['name']
        id = result['_id']
        owningOrg = getRelatedName(result['owningOrganization'])
        itOwner = getRelatedName(result['ITOwner'])
        devOwner = getRelatedName(result['developmentOwner'])
        busOwner = getRelatedName(result['businessOwner'])
        recommendation = result['mmRecommendation']
        recommendationDate = result['recommendationDate']
        location = getRelatedName(result['isLocatedInLocation'])
        productionDate = result['productionDate']
        decommissionDate = result['decommissionDate']
        print(name + ' (' + id + ')')


def getUtilities(token):
    results = makeCall(cfg.ENDPOINT + cfg.QUERYBASE + cfg.UTILQUERY, token)
    for result in results['model']:
        name = result['name']
        id = result['_id']
        owningOrg = getRelatedName(result['hasOwningOrg'])
        itOwner = getRelatedName(result['hasITOwnerUtil'])
        devOwner = getRelatedName(result['hasDevelopmentOwner'])
        busOwner = getRelatedName(result['utilHasBusinessOwner'])
        recommendation = result['recommendation']
        recommendationDate = result['recommendationDate']
        location = getRelatedName(result['primaryHostingLocationUtil'])
        print(name + ' (' + id + ')')


token = getToken()
getApplications(token)
getUtilities(token)