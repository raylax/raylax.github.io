#!/bin/env python
# encoding:utf-8

import os
import oss2
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

access_key_id = os.getenv('OSS_ACCESS_KEY_ID')
access_key_secret = os.getenv('OSS_ACCESS_KEY_SECRET')
bucket_name = os.getenv('OSS_BUCKET')
endpoint = os.getenv('OSS_ENDPOINT')
path = 'public'
path_len = len(path) + 1

auth = oss2.Auth(access_key_id, access_key_secret)
bucket = oss2.Bucket(auth, endpoint, bucket_name)


def upload(f):
    print("[*] uploading %s" % (f,))
    file = f[path_len:]
    bucket.delete_object(file)
    with open(f, 'rb') as b:
        bucket.put_object(file, b)


def list_files(p):
    files = os.listdir(p)
    for file in files:
        fp = p + '/' + file
        if os.path.isfile(fp):
            upload(fp)
        else:
            list_files(fp)


list_files(path)

