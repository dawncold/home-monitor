#! /bin/env python
# coding: utf8

import subprocess

DHT_PROGRAM_PATH = './Adafruit_DHT'
GPIO_PIN = '8'
DHT_MODEL = '11'
MAX_TRIED_COUNT = 3


def read_from_dht():
    ret = None
    tried_count = 1
    while 1:
        ret = subprocess.Popen(['sudo', DHT_PROGRAM_PATH, DHT_MODEL, GPIO_PIN]).communicate()[0]
        if ret:
            break
        tried_count += 1
        if tried_count == MAX_TRIED_COUNT:
            break

if __name__ == '__main__':
    print(read_from_dht())