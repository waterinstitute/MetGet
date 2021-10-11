#!/usr/bin/env python3
import requests
import json
from datetime import datetime
import sys

headers= {'x-api-key': 'YOUR-API-KEY'}

api_endpoint = "https://YOUR-METGET-API-ENDPOINT/build"

print("Beginning to make a request...")
domains = [ 
    { "name": "gfs-watl",
      "service": "gfs-ncep",
      "x_init": -100,
      "y_init": 3,
      "x_end": -40,
      "y_end": 50,
      "di": 0.25,
      "dj": 0.25,
      "level": 0
    },
    { "name": "nam-watl",
      "service": "nam-ncep",
      "x_init": -95,
      "y_init": 10,
      "x_end": -70,
      "y_end": 35,
      "di": 0.1,
      "dj": 0.1,
      "level": 1
    } 
]
request_data = { "version": "0.0.1", "creator": "zcobell", "background_pressure": 1013.0,
                 "nowcast": False, "multiple_forecasts": False,
                 "start_date": str(datetime(2021,9,27,0,0,0)), 
                 "end_date": str(datetime(2021,9,29,0,0,0)),
                 "time_step": 900, "domains": domains, 
                 "filename": "test_data", "format": "ascii"}

print("Begnning the build request with MetGet...")
r = requests.post(api_endpoint,headers=headers,json=request_data)
if r.status_code != 200:
    print("Request failed.")
else:
    print("Request succeeded.")
print(json.dumps(json.loads(r.text),indent=2,sort_keys=True))
