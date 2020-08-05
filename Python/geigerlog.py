# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 18:00:17 2020

@author: frederik
"""

import time
import datetime
import isotime

col_sample = 0
col_relseconds = 1
col_UTC = 2
col_cpsdev = 3
col_cpsfifo60s = 4
col_cpmLOGI = 5
col_cpmfifo15m = 6
col_LAST = col_cpmfifo15m

# col_sample = 0
# col_relseconds = 1
# col_cpsdev = 2
# col_cpsfifo60s = 3
# col_cpmfifo15m = 4
# col_UTC = 5
# col_LAST = 5

COLUMN_SEPARATOR = "; "

# defined outside of class to be useable without an instance of logfile
def mklogs(sample, relseconds, time_tup, cps_device, cps_fifo60s, cpm_LOGI, cpm_fifo15m) :
    i = 0
    s = ""
    while i <= col_LAST :
        if i == col_sample :
            s += ("{:d}{}".format(sample, COLUMN_SEPARATOR))
        elif i == col_relseconds :
            s += ("{:.1f}{}".format(relseconds, COLUMN_SEPARATOR))
        elif i == col_UTC :
            s += ("{}{}".format(isotime.iso8601.str_from_gmtuple(time_tup), COLUMN_SEPARATOR))
        elif i == col_cpsdev :
            s += ("{:d}{}".format(cps_device, COLUMN_SEPARATOR))
        elif i == col_cpsfifo60s :
            s += ("{:.3f}{}".format(cps_fifo60s, COLUMN_SEPARATOR))
        elif i == col_cpmLOGI :
            s += ("{}{}".format(cpm_LOGI, COLUMN_SEPARATOR))
        elif i == col_cpmfifo15m :
            s += ("{}{}".format(cpm_fifo15m, COLUMN_SEPARATOR))
        else :
            s += ("?{}".format(COLUMN_SEPARATOR))
        i += 1
    return s

def mkheaders() :    
    i = 0
    s = "#"
    while i <= col_LAST :
        if i == col_sample :
            s += ("Cycle{}".format(COLUMN_SEPARATOR))
        elif i == col_relseconds :
            s += ("Rel.Time[s]{}".format(COLUMN_SEPARATOR))
        elif i == col_UTC :
            s += ("YYYY-MM-DDThh:mm:ss:00:00{}".format(COLUMN_SEPARATOR))
        elif i == col_cpsdev :
            s += ("DEVICE_CPS[CPS]{}".format(COLUMN_SEPARATOR))
        elif i == col_cpsfifo60s :
            s += ("CountRate60s[CPS]{}".format(COLUMN_SEPARATOR))
        elif i == col_cpmLOGI :
            s += ("CountRate<LOGI>s[CPM]{}".format(COLUMN_SEPARATOR))
        elif i == col_cpmfifo15m :
            s += ("CountRate<MM>x60s{}".format(COLUMN_SEPARATOR))
        else :
            s += ("?{}".format(COLUMN_SEPARATOR))
        i += 1
    return s

class Logfile :
    def __init__(self):
        self.logf = None
        self.isWrite = False
     
    
    def open(self, logpath, mode="r") :
        if mode == "w" :
            self.isWrite = True
        else :
            self.isWrite = False
            
        if self.isWrite :
            try:
                self.logf = open(logpath, "w")
            except IOError :
                sys.exit("Not able to open (for write) input file "+logpath)
        else :        
            try:
                self.logf = open(logpath, "r")
            except IOError :
                sys.exit("Not able to open (for read) input file "+logpath)
        
    def close(self) :
        if self.logf :
            if self.logf.closed :
                return
            else :
                self.logf.close()
    
    def readline(self):
        items = []
        if self.isWrite:
            return []
        while True:
            try:
                s = self.logf.readline()
            except IOError :
                return []
            if len(s) < 1 :
                return []
            if s[0] == "#" :
                continue
            #print("READ",s)
            break
        items = s.split(COLUMN_SEPARATOR)
        return items

    def CPM(self, items):
        # cpm ; handle the occasional "?" instead of value
        try: 
            return float(items[col_cpmfifo15m])
        except ValueError:
            return -1        

    def CPM_LOGI(self, items):
        # cpm ; handle the occasional "?" instead of value
        try: 
            return float(items[col_cpmLOGI])
        except ValueError:
            return -1        


    def CPS(self, items):
        return float(items[col_cpsfifo60s])
 
    def UTC_String(self, items):
        return (items[col_UTC])    
    
    def UTC_Tuple(self, items) :
        s = (items[col_UTC]) 
        dt = isotime.iso8601.dt_from_str(s)
        return isotime.iso8601.gmtuple_from_dt(dt)
    
    def UTC_Hour(self, items):
        s = (items[col_UTC]) 
        dt = isotime.iso8601.dt_from_str(s)
        return int(dt.hour)    
  
    def relseconds(self, items) :
        return float(items[col_relseconds])

    def writeline(self, logs):
        if not self.isWrite:
            return []
        print(logs, file=self.logf)



# create logstring. Time string is UTC ("Zulu" / Z / +00:00) in ISO 8601 format
#     logs = "{}; {}; {}; {}; {}; {}".format(
#          d.sample, dt, time.strftime("%Y-%m-%dT%Hh%Mm%SsZ", d.t), d.DEVCPS, d.cpsf.avr(), cpms)
