"""Setup cron jobs.
"""
from __future__ import print_function
import os
import sys
import yaml
import re
import datetime as dt
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
def assignCv(cronvals,cronstr,i,val,every=False):
    "every is used for specifying  every x format."
    #print("kwIndex %r value:%r "%(i,val))
    if (i==len(cronvals)-1 and (val is float)) or (i<0):
        return
    if i<len(cronvals) and val>=limits[i][0]:
        val=int(val)
        if every and val>0:
            cronstr[i]='*/'
        if(cronvals[i]==-1):
            cronvals[i]=val
            for k in range(i):
                cronvals[k]=(limits[k][0] if cronvals[k]==-1 else cronvals[k])
        else:
            cronvals[i]+=val
def processTokens(tokens,cronstr,cronvals):
    for i in range(len(tokens)):
        if (type(tokens[i]) is float):
        #and (tokens[i-1]=='every'):
            # on every x format
            try:
                kwIndex=keyWordIndex(tokens[i+1])
                #print("Token: %r Value:%r kwIndex: %r"%(tokens[i+1],tokens[i],kwIndex))
                if (kwIndex is not None) and tokens[i]>=limits[kwIndex][0]:
                    maxval=(maxValues[kwIndex-1] if kwIndex>0 else 1)
                    x,y=splitFloat(tokens[i],maxval) # 2.5 hours => 2 hours 30 mins
                    assignCv(cronvals,cronstr,kwIndex,x%maxValues[kwIndex],True)
                    assignCv(cronvals,cronstr,kwIndex+1,x/maxValues[kwIndex],True)
                    if y>0:
                        assignCv(cronvals,cronstr,kwIndex-1,y,True)
            except Exception as e:
                print('Error processing %s\n%r'%(tokens[i],e))

def main():
    conf=yaml.safe_load(open(os.path.join(".", "rorolite.yml")).read())
    if 'cron' in conf:
        for job in conf['cron']:
            print("\nrun %s at %s"%(job['command'],job['when']))
            cronstr=['*']*5
            cronval=[-1]*5
            tokens=[]
            jobstr=[]
            for token in job['when'].split(' '):
                tokens.append(valueOf(token))
            print(tokens)
            processTokens(tokens,cronstr,cronval)
            for i in range(len(cronstr)):
                x=(str(int(cronval[i])) if cronval[i]!=-1 else '')
                y=(cronstr[i] if (x == '') or cronstr[i]!='*' else ''  )
                jobstr.append(y+x)
            jobstr=' '.join(jobstr)
            print(jobstr)
main()

#rePatters=[[],[],['month\s*([0-3]?[0-9])','([0-3]?[0-9]) of every' ],['[0-9]+\s*hours?'],['[0-9]+\s*minutes?']]

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
#
# def factorial(lst,start,end):
#     fact=1
#     if start>=0:
#         for k in range(start,end+1):
#             fact=fact*lst[k]
#     print("fact=%r"%fact)
#     return fact
#
# def inLimits(val,kwIndex):
#     try:
#         if limits[kwIndex][0]>=val and val<=limits[kwIndex][1]:
#             return True
#     except Exception as e:
#         print("Exception inLimits: %r"%e)
#     return False
# def propagate(val,kwIndex,cronvals):
#     "suppose user has given 12456 seconds. this must be translated to secs,mins,hrs"
#     print("val=%r kwI=%r crv=%r"%(val,kwIndex,cronvals))
#     kw=kwIndex
#     cronvals[kwIndex]=val%maxValues[kwIndex]
#     val=val-cronvals[kwIndex]
#     cronvals[]
#     while (not inLimits(val,kwIndex)) and val>=maxValues[kwIndex] and ++kwIndex<(len(keywords)-1):
#         try:
#             fval=factorial(maxValues,kw,kwIndex)
#             cronvals[kwIndex]=int(val/fval)
#             val=val-cronvals[kwIndex]*fval
#         except Exception as e:
#             print("Exception %r"%(e))
#
#
#
