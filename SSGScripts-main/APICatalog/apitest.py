
import requests

url = "https://apis-r.massmutual.com/rest/agreementsapi/v1/agreements"
resp = requests.get(url)

print(resp)