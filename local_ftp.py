#! /bin/env python
# coding: utf8

from ftplib import FTP
FTP_ADDRESS = '192.168.2.1'
FTP_USER = 'ftp'
FTP_PASSWORD = 'ftp'
FTP_UPLOAD_DIR = 'ftp'


def upload(name, f):
    ftp = FTP(host=FTP_ADDRESS, user=FTP_USER, passwd=FTP_PASSWORD)
    ftp.cwd(FTP_UPLOAD_DIR)
    ftp.storbinary('STOR {}'.format(name), f)
    ftp.close()