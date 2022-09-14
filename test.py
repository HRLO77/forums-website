import requests
print(requests.get('http://127.0.0.1:8000/help', data={"form":"help"}).url)