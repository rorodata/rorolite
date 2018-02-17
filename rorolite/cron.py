"""Setup cron jobs.
"""
from __future__ import print_function
import os
import sys
import yaml
import re
# class Cron:
#     def __init__(self, directory="."):
#         self.directory = directory
#         self.config = None
#     def read_config(self, root):
#         path = os.path.join(root, "rorolite.yml")
#         return yaml.safe_load(open(path).read())
#     def setup_cron(self):
#         self.conf=read_config(self.directory)
#         if 'cron' in conf:
#             for job in conf['cron']:
#                 print("\nJob description:%s"%(job['description']))

# crontab format
# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday;
# │ │ │ │ │              7 is also Sunday on some systems)
# │ │ │ │ │
# │ │ │ │ │
# * * * * *  command to execute
# 10 AM/PM, 10:55 AM/PM, saturday
daysOfWeek=['sunday','monday','tuesday','wednsday','thursday','friday','saturday']
months=['january','february','march','april','may','june','july','august','septemeber','october','november','december']

def isType(type,val):
    value=None
    try:
        value=type(val)
    except Exception:
        return False
    return value

def splitFloat(flVal,baseVal):
    temp=float(flVal)*float(baseVal)
    return (int(temp/baseVal),int(temp%baseVal))

def valueOf(val):
    v=isType(float,val)
    if v:
        return v
    v=re.search('([0-9]+)?:?([0-9]+)?\s*([apAP][mM])?',val)
    if v.group():
        return v.groups()
    return val

def main():
    conf=yaml.safe_load(open(os.path.join(".", "rorolite.yml")).read())
    if 'cron' in conf:
        for job in conf['cron']:
            print("\nrun %s at %s"%(job['command'],job['schedule']))
            jobstr=['*']*5
            tokens=[]
            for token in job['schedule'].split(' '):
                tokens.append(valueOf(token))
            print(tokens)
