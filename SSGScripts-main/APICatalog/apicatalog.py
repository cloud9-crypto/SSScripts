import requests

url = "https://apicatalog.db-api-prd.dsawsprd.massmutual.com/api/services"

resp = requests.get(url)
apis = resp.json()
print(resp)
count = 0
badcount = 0
for api in apis:
    url = api["swaggerSpecLink"]
    try:
        resp = requests.get(url)
        api['swagger'] = resp.json()
        count = count + 1
    except:
        api['swagger'] = "Error"
        badcount = badcount + 1
        print(api["name"] + " - " + api["swaggerSpecLink"] + " | Resp: " + str(resp))
print("Good: " + str(count) + " | Bad: " + str(badcount))
print(resp)