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

influxdb_config = None
influxdb_config_path = '/home/pi/.INFLUXDB_CONFIG'


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
        tem_response.raise_for_status()
        hum_response.raise_for_status()
    except requests.ConnectionError:
        print('connection error')
    except requests.HTTPError as e:
        print('invalid response: {}'.format(e.message))
    except requests.Timeout:
        print('timeout')
    except requests.TooManyRedirects:
        print('too many redirects')
    except Exception as e:
        print('other exception: {}'.format(e.message))
    else:
        print('tem data upload successfully')
        print('hum data upload successfully')

    try:
        update_influxdb(hum, tem)
    except Exception as e:
        print('failed update influxdb: {}'.format(e.message))


def update_influxdb(hum, tem):
    global influxdb_config
    global influxdb_config_path
    if not influxdb_config:
        influxdb_config = get_influxdb_config(influxdb_config_path)
    client = influxdb.InfluxDBClient(**influxdb_config)
    data = [{
        'points': [
            [tem, hum]
        ],
        'name': 'DHT11',
        'columns': ['tem', 'hum']
    }]
    client.write_points(data)


def get_influxdb_config(path):
    config = {}
    with open(path) as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        k, v = line.split('=')
        config[k] = v
    return config

if __name__ == '__main__':
    API_KEY = get_api_key()
    influxdb_config = get_influxdb_config(influxdb_config_path)
    while 1:
        upload_tem_and_hum()
        time.sleep(DATA_UPLOAD_SECONDS_INTERVAL)