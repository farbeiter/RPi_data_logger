# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 15:51:36 2020

@author: frederik
"""

import time
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import math as m
import statistics as stat
#import argparse
import getopt
import geigerlog


class myConfig :
    def __init__(self):
        self.lopgpath = ""
        self.firsts = -1
        self.lasts = -1
        self.isSetup = False
        self.writeResults = False
        
    def setup(self):
        if self.isSetup:
            print ("Setup exits without action")
            return
        self.logpath = os.path.abspath(self.logpath)
        self.filename = os.path.split(self.logpath)[-1]
        self.basepath = os.path.split(self.logpath)[0]
        frag = self.filename.split(".")
        if len(frag) == 2 and frag[1].lower() == "csv" :
            self.casename = frag[0]
        else :
            sys.exit("Expecing CSV file, instead received "+self.logpath)
        self.outdir = os.path.join(self.basepath, self.casename+".dir")
        try: 
            os.mkdir(self.outdir)
        except FileExistsError :
            pass
        self.outp = os.path.join(self.outdir, "hourly_averages.csv")
        self.outf = open(self.outp, "w")
        #self.resultp = os.path.join(self.basepath, self.resultsp)
        self.htmlp = os.path.join(self.outdir, "index.html")
        self.isSetup = True
        
        
        
class myResults:
    def __init__(self):
        self.samplist = []
        self.cpmlist = []
        self.cpmlogilist = []
        self.hlist = []
        self.cpmhlist = []
        

def printResults(cfg, res, label) :
    if not os.path.exists(cfg.resultp) :
        resultf = open(cfg.resultp, "w")
        print("#label", "total_counts", "uncertainty", "mean", "median", "stdev", "min", "max",
              "fit_offs", "fit_slope", "logfile", "t1", "t2",
              file=resultf, sep="; ")
    else :
        resultf = open(cfg.resultp, "a")
    print(label, r.totalcounts, r.countuncert, r.mean, r.median, r.stdev, r.min, r.max, 
          r.coeff[0], r.coeff[1], cfg.logpath, cfg.firsts, cfg.lasts,
          file=resultf, sep="; ")
    resultf.close()

def printHTML(cfg, res) :
    htmlf = open(cfg.htmlp, "w")
    print("<html><body><h1>Geiger Counter logfile evaluation</h1>", file=htmlf)
    print("<p>Evaluated file : ", cfg.logpath, "</p>", file=htmlf)
    print("<p>Specified time interval : [{} ... {}] s: </p>".format(cfg.firsts, cfg.lasts), file=htmlf)
    print("<table><tr><th>Variable</th><th>Value</th><th>Unit</th></tr>", file=htmlf)
    print("<tr><td>{}</td><td>{:g}</td><td>{}</td></tr>".format(
            "Measured samples", len(r.cpmlist), " minute intervals)"), file=htmlf)
    print("<tr><td>{}</td><td>{:g}</td><td>{}</td></tr>".format(
            "Total counts", r.totalcounts, " counts"), file=htmlf)
    print("<tr><td>{}</td><td>{:g}</td><td>{}</td></tr>".format(
            "Count uncertainty (abs.)", m.sqrt(r.totalcounts), " counts"), file=htmlf)
    print("<tr><td>{}</td><td>{:g}</td><td>{}</td></tr>".format(
            "CPM Mean", r.mean, " CPM (Counts Per Minute)"), file=htmlf)
    print("<tr><td>{}</td><td>{:g}</td><td>{}</td></tr>".format(
            "CPM Median", r.median, " CPM"), file=htmlf)
    print("<tr><td>{}</td><td>{:g}</td><td>{}</td></tr>".format(
            "St.Dev. of sample", r.stdev, " CPM"), file=htmlf)
    print("<tr><td>{}</td><td>{:g}</td><td>{}</td></tr>".format(
            "Min CPM sample", r.min, " CPM"), file=htmlf)
    print("<tr><td>{}</td><td>{:g}</td><td>{}</td></tr>".format(
            "Max CPM sample", r.max, " CPM"), file=htmlf)
    print("<tr><td>{}</td><td>{:g}</td><td>{}</td></tr>".format(
            "Fit line offset", r.coeff[0], " CPM"), file=htmlf)
    print("<tr><td>{}</td><td>{:g}</td><td>{}</td></tr>".format(
            "Fit line slope", r.coeff[1]*3600, " CPM/hour"), file=htmlf)
    print("</table>", file=htmlf)
    print("<p><img src='timeseries.png'></p>", file=htmlf)
    print("<p><img src='histogram.png'></p>", file=htmlf)
    print("</body></html>", file=htmlf)
    htmlf.close()
    
def usage():
    print("\npython3 geigerLogReport.py -i <infile> [-f <t1>] [-l <t2>] [-r <resultfile>]" )
    print("Perform statistical analysis of Geiger-Müller counter data and write HTML report file\n")
    print("\t-i <infile> : input logfile")
    print("\t-f <t1> : start of to be evaluated time interval [<t1>...<t2>] (seconds)")
    print("\t-l <t2> : end of to be evaluated time interval [<t1>...<t2>] (seconds)")
    print("\t-r <resultfile> : Specify if resultfile should be written to <resultfile>\n")

def options(cfg):
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:f:l:r:h", ["infile=", "path=", "file=", "firsts=", "lasts=", "results="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    cfg.logpath = ""
    cfg.firsts = -1
    cfg.lasts = -1
    for o, a in opts:
        if o in ["-i", "--infile", "--path", "--file"]:
            cfg.logpath = a
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-f", "--firsts"):
            cfg.firsts = float(a)
        elif o in ("-l", "--lasts"):
            cfg.lasts = float(a)
        elif o in ("-r", "--results"):
            cfg.writeResults = True
            cfg.resultp = a
            if cfg.resultp == "" or cfg.resultp[0] == "-":
                cfg.resultp = "results.csv"
        else:
            assert False, "unhandled option"
    if cfg.logpath == "" :
        usage()
        sys.exit(2)   

### MAIN
    
 
       
cfg = myConfig()
options(cfg)
cfg.setup()
log = geigerlog.Logfile()
log.open(cfg.logpath)
r = myResults()

avrsum = 0
avrnum = 0
currenthour = -1
linenum = 0

while True :
    items=log.readline()
    #print(items)
    if len(items) < 1 :
        break # EOF
        
    seconds = log.relseconds(items)
    if cfg.lasts > 0 and seconds > cfg.lasts: # reached end of specified time interval
        break
    if seconds < cfg.firsts : # not yet in specified time interval
        continue
    
    cpm = log.CPS(items)*60.0 # log.CPS returns the CPS averaged over 60s
    if cpm < 0 :
        continue
    
    cpmlogi = log.CPM_LOGI(items) 
    
    readhour = log.UTC_Hour(items)
    avrsum += cpmlogi 
    avrnum += 1
    r.cpmlist.append(cpm)
    r.cpmlogilist.append(cpmlogi)
    r.samplist.append(log.relseconds(items))
    
    # first time
    if currenthour == -1 : # init
        refdate = log.UTC_String(items).split(":")[0]+":00:00"
        datelabel = log.UTC_String(items)
        refseconds = log.relseconds(items)
        firstsecond = refseconds
        lastitems = items
    
    # change of hour
    if readhour != currenthour :
        if not currenthour == -1 :
            refdate = items[geigerlog.col_UTC].split(":")[0]+":00:00"
            refseconds = log.relseconds(lastitems)
            avrval = avrsum / avrnum # hourly average
            r.cpmhlist.append(avrval)
            r.hlist.append(refseconds)
            print("{}; {}; {}; {};".format(linenum, refseconds, avrval, refdate), file=cfg.outf)
        currenthour = readhour
        avrsum = 0.0
        avrnum = 0
        linenum +=1
        
    lastitems = items
        
log.logf.close()
cfg.outf.close()

# Statistical evaluation
r.min = min(r.cpmlist)
r.max = max(r.cpmlist)
r.mean = stat.mean(r.cpmlist)
r.median = stat.median(r.cpmlist)
r.stdev = stat.stdev(r.cpmlist)
r.totalcounts = sum(r.cpmlist)
r.countuncert = m.sqrt(r.totalcounts)
r.coeff = list(np.polyfit(r.samplist, r.cpmlist, deg=1))
r.coeff.reverse()
tfit = [r.samplist[0], r.samplist[-1]]
cpmfit = [r.coeff[0]+t*r.coeff[1] for t in tfit]
if cfg.writeResults:
    printResults(cfg, r, datelabel)


plt.clf()
plt.figure(figsize = (10, 6))
plt.hist(r.cpmlist, bins = int(0.25*m.sqrt(len(r.cpmlist)+1)))
plt.title("Histogram")
plt.xlabel("CPM value")
plt.ylabel("Number of minute intervals")
plt.grid(True)
#plt.show()
plt.savefig(os.path.join(cfg.outdir, "histogram.png"))

plt.clf()
plt.title("Time Series Data")
plt.ylabel("CPM")
plt.xlabel("Seconds in logfile")
plt.plot(r.samplist, r.cpmlist)
plt.plot(r.hlist, r.cpmhlist, "s")
plt.plot(tfit, cpmfit)
plt.grid(True)
#plt.show()
plt.savefig(os.path.join(cfg.outdir, "timeseries.png"))

printHTML(cfg, r)

