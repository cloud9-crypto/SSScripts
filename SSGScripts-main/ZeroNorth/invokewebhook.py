import requests

url = 'https://api.zeronorth.io/v1/run/webhook/IEpwfda1SESxOTjTKFP-Aw/dGG8CA7wS_-j4-K8fy8gMw'
headers = {'Content-Type': 'application/json'}
resp = requests.get(url, headers=headers)
print(resp)