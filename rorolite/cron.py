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
#rePatters=[[],[],['month\s*([0-3]?[0-9])','([0-3]?[0-9]) of every' ],['[0-9]+\s*hours?'],['[0-9]+\s*minutes?']]

keywords = ['min(ute)?s?', 'hours?', '', 'months?', '[a-zA-Z]{3,5}days?']
daysOfWeek = ['sunday', 'monday', 'tuesday', 'wednsday', 'thursday', 'friday', 'saturday']
months = ['january','february','march','april','may','june','july','august','septemeber','october','november','december']
limits = [[0,59], [0,23], [1,31], [1,12], [0,6]]
maxValues = [60, 24, 31, 12, 7]

def keyWordIndex(str):
    for i in range(len(keywords)):
        if re.search(keywords[i],str):
            return i;
    return False

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

def factorial(lst,i):
    fact=1
    if i>=0:
        for k in range(i):
            fact=fact*lst[k]
    return fact

def propagate(val,kwIndex,cronvals):
    "suppose user has given 12456 seconds. this must be translated to secs,mins,hrs"
    cronvals[kwIndex]=val%maxValues[kwIndex]
    val=val-cronvals[kwIndex]
    while val>=0 and ++kwIndex<len(keywords-1):
        cronvals[kwIndex]=int(val/fact(maxValues,kwIndex))
        val=val-cronvals[kwIndex]


def processTokens(tokens,cronstr,cronvals):
    for i in range(1,len(tokens)):
        if (type(tokens[i]) is float) and (tokens[i-1]=='every'):
            # on every x format
            try:
                kwIndex=keyWordIndex(tokens[i+1])
                if kwIndex and tokens[i]>=limits[kwIndex][0]:
                    if tokens[i]<=limits[kwIndex][1]:
                        cronstr[kwIndex]='*/'
                        cronvals[kwIndex]=tokens[i]
                    elif kwIndex<(len(keywords)-1):
                        propagate(tokens[i],kwIndex,cronvals)
            except Exception as e:
                print('Error processing %s \n %r'%(tokens[i],e))

def main():
    conf=yaml.safe_load(open(os.path.join(".", "rorolite.yml")).read())
    if 'cron' in conf:
        for job in conf['cron']:
            print("\nrun %s at %s"%(job['command'],job['schedule']))
            cronstr=['*']*5
            cronvals=[-1]*5
            tokens=[]
            for token in job['schedule'].split(' '):
                tokens.append(valueOf(token))
            print(tokens)
            processTokens(tokens,cronstr,cronvals)
            jobstr=[ cronstr[i]+str(cronvals[i]) for i in range(5)]
            print(jobstr)
