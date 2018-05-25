#-*- coding:utf-8 -*-

import os
import datetime

log_file = os.path.dirname(os.path.realpath(__file__)) + '/../.log.txt'


def log(msg, *argv):
    fd = open(log_file, 'a')
    now = datetime.datetime.now()
    msg = str(now) + ':' + msg + '\n'
    for arg in argv:
        if hasattr(arg, '__str__'):
            msg += str(arg) + '\n'
        elif hasattr(arg, '__repr__'):
            msg += repr(arg) + '\n'
    
    fd.write(msg + '\n')
