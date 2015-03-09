#! /bin/env python
# coding: utf8

import subprocess
from datetime import datetime
import time
import json
import requests
import influxdb

DHT_PROGRAM_PATH = './Adafruit_DHT'
GPIO_PIN = '4'
DHT_MODEL = '11'
MAX_TRIED_COUNT = 3
TEM_API_URL = 'http://api.yeelink.net/v1.0/device/4315/sensor/6194/datapoints'
HUM_API_URL = 'http://api.yeelink.net/v1.0/device/4315/sensor/6195/datapoints'
API_KEY = None
API_KEY_PATH = '/home/pi/.API_KEY'
DATA_UPLOAD_SECONDS_INTERVAL = 20

INFLUXDB_HOST = 'linode.youth2009.org'
INFLUXDB_PORT = 8086
INFLUXDB_USERNAME = 'root'
INFLUXDB_PASSWORD = 'goVeil2011!'
INFLUXDB_NAME = 'rasp'


def get_api_key():
    global API_KEY
    if not API_KEY:
        try:
            API_KEY = open(API_KEY_PATH).read().strip()
        except IOError:
            print('can not read API KEY from file, please check the file is here')
            exit(-1)
    return API_KEY


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
    tem, hum = int(tem), int(hum)
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
    try:
        tem_response = requests.post(TEM_API_URL, data=json.dumps(tem_payload), headers=headers)
        hum_response = requests.post(HUM_API_URL, data=json.dumps(hum_payload), headers=headers)
    except requests.ConnectionError:
        print('connection error')
    except requests.HTTPError:
        print('invalid response')
    except requests.Timeout:
        print('timeout')
    except requests.TooManyRedirects:
        print('too many redirects')
    except Exception:
        print('other exception')
    else:
        if tem_response.status_code == 200:
            print('tem data upload successfully')
        else:
            print(tem_response.raise_for_status())
        if hum_response.status_code == 200:
            print('hum data upload successfully')
        else:
            print(tem_response.raise_for_status())

    try:
        update_influxdb(hum, tem)
    except Exception as e:
        print('failed update influxdb: {}'.format(e.message))


def update_influxdb(hum, tem):
    client = influxdb.InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT, username=INFLUXDB_USERNAME,
                                     password=INFLUXDB_PASSWORD, database=INFLUXDB_NAME)
    data = [{
        'points': [
            [tem, hum]
        ],
        'name': 'DHT11',
        'columns': ['tem', 'hum']
    }]
    client.write_points(data)

if __name__ == '__main__':
    API_KEY = get_api_key()
    while 1:
        upload_tem_and_hum()
        time.sleep(DATA_UPLOAD_SECONDS_INTERVAL)