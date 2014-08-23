#! /bin/env python
# coding: utf8

import subprocess
from datetime import datetime
import time
import json
import requests

DHT_PROGRAM_PATH = './Adafruit_DHT'
GPIO_PIN = '8'
DHT_MODEL = '11'
MAX_TRIED_COUNT = 3
TEM_API_URL = 'http://api.yeelink.net/v1.0/device/4315/sensor/6194/datapoints'
HUM_API_URL = 'http://api.yeelink.net/v1.0/device/4315/sensor/6195/datapoints'
API_KEY = '6c5380ac5abd272614dfd77ace7b6139'
DATA_UPLOAD_SECONDS_INTERVAL = 20


def read_from_dht():
    ret = None
    tried_count = 1
    while 1:
        ret = subprocess.check_output(['sudo', DHT_PROGRAM_PATH, DHT_MODEL, GPIO_PIN])
        if ',' in ret:
            break
        tried_count += 1
        if tried_count == MAX_TRIED_COUNT:
            break
    return ret


def upload_tem_and_hum():
    try:
        tem, hum = read_from_dht().split(',')
    except ValueError:
        print('can not read data from dht, waiting for next retrieve')
        return
    timestamp = datetime.now().isoformat()
    headers = {
        'U-ApiKey': API_KEY
    }
    tem_payload = {
        'timestamp': timestamp,
        'value': tem
    }
    hum_payload = {
        'timestamp': timestamp,
        'value': hum
    }
    tem_response = requests.post(TEM_API_URL, data=json.dumps(tem_payload), headers=headers)
    hum_response = requests.post(HUM_API_URL, data=json.dumps(hum_payload), headers=headers)
    if tem_response.status_code == 200:
        print('tem data upload successfully')
    else:
        print(tem_response.raise_for_status())
    if hum_response.status_code == 200:
        print('hum data upload successfully')
    else:
        print(tem_response.raise_for_status())

if __name__ == '__main__':
    while 1:
        upload_tem_and_hum()
        time.sleep(DATA_UPLOAD_SECONDS_INTERVAL)