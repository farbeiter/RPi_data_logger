# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 18:00:17 2020

@author: frederik
"""

import time
import datetime
#from datetime import datetime, timezone


UTC_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S+00:00'


class iso8601:
    
    def replace_zulu(s):
        return s.replace('Z', '+00:00')
    
    def dt_from_gmtuple(tup):
        dt =  datetime.datetime(tup.tm_year, tup.tm_mon, tup.tm_mday,
                                 tup.tm_hour, tup.tm_min, tup.tm_sec,
                                 tzinfo=datetime.timezone.utc)
        return dt
    
    def tuple_from_dt(dt):
        return dt.timetuple()

    def gmtuple_from_dt(dt):
        return dt.utctimetuple()
    # what is  datetime.timetz()¶

    
    def str_from_dt(dt):
        return dt.astimezone(datetime.timezone.utc).replace(microsecond=0).isoformat()
    
    def str_from_gmtuple(tup):
        dt = iso8601.dt_from_gmtuple(tup)
        return iso8601.str_from_dt(dt)
    
    def dt_from_str(s):
        s.strip()
        s = iso8601.replace_zulu(s.replace("\n", ""))
        dt = datetime.datetime.fromisoformat(s)
        return dt
    
    def dt_from_sec(sec):
        datetime.datetime.fromtimestamp(sec, datetime.timezone.utc)
    
    def gmtuple_from_sec(sec):
        return time.gmtime(sec)
    
    def sec_from_gmtuple(tup):
        return time.mktime(tup)

    def sec_from_dt(dt):
        return datetime.timestamp(dt)       
        
