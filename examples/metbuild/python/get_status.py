#!/usr/bin/env python3
import requests
import json
from datetime import datetime
import sys

headers= {'x-api-key': 'YOUR-API-KEY'}

api_endpoint = "https://YOUR-METGET-API-ENDPOINT/status"

print("Beginning status request with MetGet...")
r = requests.get(api_endpoint,headers=headers)
if r.status_code != 200:
    print("Request failed.")
else:
    print("Request succeeded.")
print(json.dumps(json.loads(r.text),indent=2,sort_keys=True))
sys.exit(0);
