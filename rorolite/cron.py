"""Setup cron jobs.
"""
from __future__ import print_function
import os
import sys
import yaml
import re

# crontab format
# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday)
# │ │ │ │ │              7 is also Sunday on some systems)
# │ │ │ │ │
# │ │ │ │ │
# * * * * *  command to execute

keywords = ['min(ute)?s?', 'hours?', '', 'months?', '']
skipWords=['min','minute','minutes''every','day','at','on','everyday','month','hour','months','hours','daily']
daysAndMonths={
    3 : ['','january','february','march','april','may','june','july','august','septemeber','october','november','december'],
    4 : ['sunday', 'monday', 'tuesday', 'wednsday', 'thursday', 'friday', 'saturday']
}
valRegex=['([0-9]+):([0-9]+)\s*([apAP][mM])?','([0-9]+):?([0-9]+)?\s*([apAP][mM])','([0-3]?[0-9])(st|th|rd)']
limits = [[0,59], [0,23], [1,31], [1,12], [0,6]]
maxValues = [60, 24, 31, 12, 7]

def inLimits(val,kwIndex):
    try:
        if val>=limits[kwIndex][0] and val<=limits[kwIndex][1]:
            return True
    except Exception as e:
        print("inLimits:",str(e))
    return False

def keyWordIndex(str):
    for i in range(len(keywords)):
        if re.search(keywords[i],str,re.I):
            return i
    return False

def isType(type,val):
    value=None
    try:
        value=type(val)
    except Exception:
        return False
    return True

def splitFloat(flVal,baseVal):
    temp=float(flVal)*float(baseVal)
    return (int(temp/baseVal),int(temp%baseVal))

def valueOf(val):
    try:
        if isType(float,val):
            return float(val)
        for regex in valRegex:
            g=re.search(regex,val)
            if g and g.group():
                return g.groups()
    except Exception as e:
        print("Exception at valueOf with %r %r"%(val,e))
    return val
def assignCv(cronvals,cronstr,i,val,every=False):
    "every is used for specifying  every x format."
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

def lookForDayOfMonth(tokens,k):
    if k>=0 and k<len(tokens):
        if (type(tokens[k]) is float) and  inLimits(tokens[k],2):
            tokens[k]=[int(tokens[k])]

def processTokens(tokens,cronstr,cronvals):
    for i in range(len(tokens)):
        currentToken=tokens[i]
        if type(currentToken) is float and i+1<len(tokens):
            # 'every x' format
            try:
                kwIndex=keyWordIndex(tokens[i+1])
                if (kwIndex is not None) and currentToken>=limits[kwIndex][0]:
                    maxval=(maxValues[kwIndex-1] if kwIndex>0 else 1)
                    x,y=splitFloat(currentToken,maxval) # 2.5 hours => 2 hours 30 mins
                    assignCv(cronvals,cronstr,kwIndex,x%maxValues[kwIndex],True)
                    assignCv(cronvals,cronstr,kwIndex+1,x/maxValues[kwIndex],True)
                    if y>0:
                        assignCv(cronvals,cronstr,kwIndex-1,y,True)
            except Exception as e:
                print('Error processing %s %r on line %r'%(currentToken,e,sys.exc_info()[-1].tb_lineno))
        elif type(currentToken) is str:
            if currentToken in skipWords : # skip day, everyday,month etc
                continue

            for key,value in daysAndMonths.items():
                for k in range(len(value)):
                    if currentToken.lower() in value[k]: # apr,april,wed,wednsday etc. are valid
                        try:
                            cronvals[int(key)]=k
                            #lookForDayOfMonth(tokens,i-1)
                            #lookForDayOfMonth(tokens,i+1)
                        except Exception as e:
                            print(str(e))
        elif type(currentToken) is tuple:
            temp=currentToken
            temp=[(int(e) if isType(int,e) else e)  for e in temp]
            temp=[(0 if e is None else e)  for e in temp]
            currentToken=tuple(temp)
            if len(currentToken)==3: #time
                currentToken=(currentToken[1], currentToken[0], currentToken[2])
                for v in range(len(currentToken)-1):
                    if inLimits(currentToken[v],v):
                        cronvals[v]=currentToken[v]
                amPmStr=currentToken[len(currentToken)-1]
                if amPmStr and amPmStr.lower() == 'pm':
                    cronvals[1]=(cronvals[1]+12)%24
            elif len(currentToken)==2:
                 if inLimits(currentToken[0],2):
                     cronvals[2]=currentToken[0]

def setupCron():
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
setupCron()

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
#
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
