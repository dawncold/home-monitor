#! /bin/env python
# coding: utf8
import subprocess
import sys
import tempfile
import time
from datetime import datetime
import RPi.GPIO as GPIO
import local_ftp


CAMERA_PROGRAM = 'raspistill'
GPIO_SOCKET_NUMBER = 26


def get_image_bytes():
    return subprocess.check_output([CAMERA_PROGRAM, '-o', '-'])


def install():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(GPIO_SOCKET_NUMBER, GPIO.IN)


def uninstall():
    GPIO.cleanup(GPIO_SOCKET_NUMBER)


def detect_loop():
    while 1:
        if GPIO.input(GPIO_SOCKET_NUMBER):
            print('capture...')
            capture()
        time.sleep(2)


def capture():
    try:
        image_bytes = get_image_bytes()
    except Exception:
        print('get image bytes failed')
    else:
        with tempfile.TemporaryFile(mode='wb+') as f:
            f.write(image_bytes)
            f.seek(0)
            while 1:
                try:
                    local_ftp.upload(datetime.now().strftime(''), f)
                except Exception:
                    print('upload failed, retry')
                else:
                    break


if __name__ == '__main__':
    try:
        install()
    except Exception:
        print('setup GPIO failed')
        try:
            install()
        except Exception:
            print('uninstall GPIO failed')
        sys.exit(-1)
    else:
        try:
            detect_loop()
        except Exception:
            uninstall()
