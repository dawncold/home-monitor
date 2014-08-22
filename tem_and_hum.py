#! /bin/env python
# coding: utf8

import subprocess

DHT_PROGRAM = 'Adafruit_DHT'
GPIO_PIN = 4
DHT_MODEL = 11


def read_from_dht():
    ret = None
    while 1:
        ret = subprocess.Popen(['sudo', DHT_PROGRAM, DHT_MODEL, GPIO_PIN]).communicate()[0]
        if ret:
            break

if __name__ == '__main__':
    print(read_from_dht())