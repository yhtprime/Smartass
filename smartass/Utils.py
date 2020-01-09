import os
from uuid import uuid4

PIC_URL = '/static/pic/'
FACEDATA_URL = '/static/facedata/'
PENGYOU_URL = '/static/pengyou/'

#生成随机名字
def makerandomuuid(ext):
    filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return filename