import sys
import serial
import time
from datetime import datetime

import mygpio
import fifo
import geigerlog

import math as m
#import isotime
#import keyboard

OVERRIDE_SWITCHES = False # will assume all switches are active. Useful if no switchboard connected
SIMULATE_GEIGER = False # will simulate Geiger counter readings with 1.0 CPS
SIMULATED_SERLINE = "CPS, 1, CPM, 60, uSv/hr, 0.0, SLOW"

class configData:
     def __init__(self):
          self.wwwdir = "/home/pi/public_html/" #"/var/www/html/"
          #self.htmlfname ="dl.html"
          self.logdir = "/home/pi/public_html/"
          self.logfname = "log.csv"
          self.isLogging = False
          self.isAveraging = False
          #self.multimin_cpmfifosize = 15
          self.logInterval = 60 # number of cycles between two log writes
          self.createHtml = True # set true if you wish HTML output; then make sure to have permissions for the output directory
          self.createFigure = True # set true if the HTML page should include a figure made by pyplot
          self.levelHigh = 40 # Threshold level for yellow "alarm" LED

class loggerData:
     def __init__(self):
         self.gcycle = 0
         #self.t 
         self.DEVCPS = 0
         self.DEVCPM = 0
         self.minute_cpsf = fifo.fifo(60) # this FIFO contains the last 60 DEVCPS samples ("1 minute")
         self.multimin_cpmf = fifo.fifo(15) # this FIFO contains multiple minutes
         #self.logif = fifo.dFifo(1) # temporary sizing
         #self.cp15mf = fifo.numFifo(4*24)
         self.avrcounts = 0 # counts accumulated over the arbitrary averaging period
         self.avrcycles = 0
         self.avrdt = 0 # (running) averaging time period 
         self.avrcpm_dt = 0.0  # result of average in CPM
         self.avrcpm_cyc = 0.0
         self.avrreldev = 0.0 # relative uncertainty of average based on number of counts, 1/sqrt(counts)
         self.logblocknum = 0
         self.logcyc = 0 #cycles since the last logfile write
         self.lccounts = 0.0 # counts since the last logfile write

 


def printHtmlPage(conf, data, figupdate=True):
     
     # prepare the PNG figure
     if conf.createFigure and figupdate :
          plt.clf()
          plt.plot(range(data.multimin_cpmf.num()), data.multimin_cpmf.all())
          plt.xlabel('Minutes ago')  
          plt.ylabel('FIFO CPM')  
          plt.savefig(conf.wwwdir+"fig.png")
          plt.close()

     # write out the HTML page
     outf = open(conf.wwwdir+"data.html", "w")
     print("<html>", file=outf)
     print("<body>", file=outf)
     print("<h1>Geiger Datalogger</h1>", file=outf)
     print("<h2>Device</h2>", file=outf)
     print("<p><ul>", file=outf)
     print("<li> cycle # = ", data.gcycle, "</li>", file=outf)
     print("<li> UCT date time = ", time.strftime("UTC_%Y-%m-%d_%Hh%Mm%Ss", d.t), "</li>", file=outf)
     print("<li> CPS = ", data.DEVCPS, "</li>", file=outf)
     print("<li> CPM = ", data.DEVCPM, "</li>", file=outf)
     print("</ul></p>", file=outf)
     print("<h2>FIFO</h2>", file=outf)
     print("<p><ul>", file=outf)
     print("<li>", file=outf)
     for cpm in data.multimin_cpmf.all() :
         print("{} ;".format(cpm), file=outf)
     print("</li>", file=outf)
     print(f"<li> Avr. CPS*60({data.minute_cpsf.num()}s) = {data.minute_cpsf.avr()*60} +/- {data.minute_cpsf.stdev()*60} </li>", file=outf)
     print(f"<li> Avr. CPM({data.multimin_cpmf.num()}min) = {data.multimin_cpmf.avr()} +/- {data.multimin_cpmf.stdev()} </li>", file=outf)
     print("</ul></p>", file=outf)
     if conf.createFigure :
         print("<img src=\"fig.png\">", file=outf)
     print("<h2>Average and Logfile</h2>", file=outf)
     
     if cfg.isAveraging :
          print("<p> Averaging is ON. (Block={}) Current values ;</p>".format(data.logblocknum), file=outf)
          print("<p><ul><li>cycles={:d}</li><li>time interval dt={:g}</li><li>counts={:d}</li> <li>cpm(cyc)={:.3g}</li> <li>cpm(dt)={:.3g}</li> <li>1/sqrt(counts)={:.3g}</li></ul></p>".format(
               data.avrcycles, data.avrdt, data.avrcounts, data.avrcpm_cyc, data.avrcpm_dt, data.avrreldev) , file=outf)
     else :
          print("<p> Averaging is OFF. Last values : </p>", file=outf)
          print("<p><ul><li>cycles={:d}</li><li>time interval dt={:g}</li><li>counts={:d}</li> <li>cpm(cyc)={:.3g}</li> <li>cpm(dt)={:.3g}</li> <li>1/sqrt(counts)={:.3g}</li></ul></p>".format(
               data.avrcycles, data.avrdt, data.avrcounts, data.avrcpm_cyc, data.avrcpm_dt, data.avrreldev) , file=outf)
          
     if cfg.isLogging :
          print("<p> Logging to {} (block={})</p>".format(cfg.logfname, data.logblocknum), file=outf)
     else  :
          print("<p> Not logging. Last logfile was {} </p>".format(cfg.logfname), file=outf)
     print("</body>", file=outf)
     
     outf.flush()
     outf.close()
     


### MAIN
     
#
# Initialization
#

cfg = configData()
d = loggerData()
#d.logif.dim(cfg.logInterval)
mio = mygpio.myGPIO()
lf = geigerlog.Logfile()

if cfg.createFigure: # this takes 10s to load on a raspberry 1 A+ !!!
    import matplotlib.pyplot as plt

ser = serial.Serial(
               port="/dev/serial0",
               baudrate = 9600,
               parity=serial.PARITY_NONE,
               stopbits=serial.STOPBITS_ONE,
               bytesize=serial.EIGHTBITS,
               timeout=30
           )
           
# Wait for the geiger counter to deliver serial output. Signal LEDs as "ready"
mio.serLed(True)
mio.logLed(True)
mio.highLed(True)
print("#Adjust clock, connect&switch-on Geiger counter, then activate switch #4 to proceed")
while True :
     if SIMULATE_GEIGER :
         serial_line = SIMULATED_SERLINE
     else :
         serial_line = ser.readline()
     mio.serLed(False)
     time.sleep(0.05) # just to see the LED blink
     items = str(serial_line).split(",")
     switches = mio.readSwitches()
     if len(items) == 7 and (switches[3] or OVERRIDE_SWITCHES) : # checking if S4 is activated
          break
        
mio.serLed(False)
mio.logLed(False)
mio.highLed(False)

# now register "zero time"          
if not SIMULATE_GEIGER:
    serial_line = ser.readline() # flush the serial buffer
cfg.birth = time.gmtime() # make sure the RPi clock is adjusted (via network) before this program is called !!!
bseconds = time.mktime(cfg.birth)
print("### UTC Times relative to ", cfg.birth)

d.gcycle = 0 # global counter incrementing for each CPS sample taken
loopsec = 0 # cycling counter 0...59

#
# "Infinite loop" to measure, pre-process, log and display the data
#

while 1 :
     # read serial output from migthyohm geiger counter
     mio.serLed(True)
     if not SIMULATE_GEIGER :
         serial_line = ser.readline() # "real" reading 
     else :
         serial_line = SIMULATED_SERLINE # use for testing without geiger counter
         time.sleep(0.9) 
     d.t = time.gmtime()
     mio.serLed(False)
     time.sleep(0.05) # just to see the LED blink
     tseconds = time.mktime(d.t)
     dt = tseconds - bseconds
     # analyse the serial output string
     items = str(serial_line).split(",")
     if len(items) != 7 :
          continue
     d.DEVCPS = int(items[1].strip())
     d.DEVCPM = int(items[3].strip())
     #time.sleep(1)

     # the minute_cpsf FIFO always holds the last 60 cycles, unit CPS
     d.minute_cpsf.put(d.DEVCPS)
     
     #cyccpms is the CPM averaged over on log interval
     if cfg.isLogging :
         d.lccounts += d.DEVCPS
         d.logcyc += 1
         cyccpms = "{:.2f}".format(60.0 * d.lccounts / float(d.logcyc))
     else :
         cyccpms = "0.0"
     
     # multicpms is the CPM averaged over several minutes, by default 15
     if d.multimin_cpmf.num() < 1 :
           multicpms = "{:.2f}".format(d.minute_cpsf.avr()*60)
     else :
           multicpms = "{:.2f}".format(d.multimin_cpmf.avr())
          
     # create logstring. Time string is UTC ("Zulu" / Z / +00:00) in ISO 8601 format
     logs = geigerlog.mklogs(d.gcycle, dt, d.t, d.DEVCPS, d.minute_cpsf.avr(), cyccpms, multicpms)
     #print("\n", serial_line)
     print(logs)

     loopsec += 1
     
     #readout the switches and start/stop requested actions
     [reqLog, reqAvr, enableHtml, s4] = mio.readSwitches()
     if OVERRIDE_SWITCHES :
         reqLog = True
         reqAvr = True
         enableHtml = True
         s4 = True
     
     if not cfg.isAveraging and reqAvr : # start new average
          d.avrcounts = 0
          d.avrcycles = 0
          d.avrt0 = tseconds - 1.0
          d.logblocknum += 1
          print(" # start averaging")
          cfg.isAveraging = True
          if cfg.isLogging and not lf.logf.closed :
              lf.writeline("\n\n# START block number {} (averaging ON)".format(d.logblocknum))
          
          
     if cfg.isAveraging and not reqAvr : # stop averaging
          cfg.isAveraging = False
          print("stopped averaging")
          if cfg.isLogging and not lf.logf.closed :
              lf.writeline("# STOP averaging for block number {} here ; counts={} cycles={}".format(
                  d.logblocknum, d.avrcounts, d.avrcycles))
          
     if cfg.isAveraging :
          d.avrcounts += d.DEVCPS
          d.avrdt = tseconds - d.avrt0
          d.avrcycles += 1
          if d.avrdt > 0 :
               d.avrcpm_dt = float(d.avrcounts*60.0) / d.avrdt
               d.avrcpm_cyc = float(d.avrcounts*60.0) / float(d.avrcycles) 
          else :
               d.avrcmp = 0.0
               wurzel = 0
          wurzel = m.sqrt(d.avrcounts)
          if wurzel > 0 :
               d.avrreldev = 1.0/wurzel
          else :
               d.avrreldev = 0.0
          print("# AVR : cyc={:d} dt={:g}, sum={:d}, cpm(cyc)={:.3g}, cpm(dt)={:.3g}, sqrt(sum)={:.3g}, 1/sqrt(sum)={:.3g}".format(
               d.avrcycles, d.avrdt, d.avrcounts, d.avrcpm_cyc, d.avrcpm_dt, wurzel, d.avrreldev) )

     if cfg.isLogging :
          #d.logcyc += 1
          if d.logcyc >= cfg.logInterval :
               mio.logLed(True)
               lf.writeline(logs)
               lf.logf.flush()
               time.sleep(0.05) # just to see the LED blink
               mio.logLed(False)
               d.logcyc = 0
               d.lccounts = 0.0
               
     if not cfg.isLogging and reqLog : # start new logfile
          t = time.localtime()
          utc = time.gmtime()
          cfg.logfname = "{}{:04d}-{:02d}-{:02d}_{:02d}h{:02d}m{:02d}s_log.csv".format(
               cfg.logdir, t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
          print("#Starting new logfile ", cfg.logfname)
          lf.open(cfg.logfname, "w")
          #outf = open(cfg.logfname, "w")
          if not lf.logf.closed : # successfully opened new file
               cfg.isLogging = True
               lf.writeline("# Started logging at localtime {}".format(t))
               lf.writeline("# (UTC : {}".format(utc))
               lf.writeline("# The interval between two log entries is LOGI={} cycles".format(cfg.logInterval))
               lf.writeline("# The number of 60s intervals in the multi-minute FIFO is MM={}".format(d.multimin_cpmf.num()))
               lf.writeline(geigerlog.mkheaders())
          d.logcyc = 0
          d.lccounts = 0.0
               
     if cfg.isLogging and not reqLog : # stop logging
          t = time.localtime()
          utc = time.gmtime()
          print("# Closing logfile ", cfg.logfname)
          lf.writeline("# Stopped logging at localtime {}".format(t))
          lf.writeline("# (UTC : {}".format(utc))
          lf.close()
          cfg.isLogging = False

     d.gcycle += 1 # increment global cycle counter
     
     if loopsec > 59 :
          d.multimin_cpmf.put(d.minute_cpsf.sum()) # transfer the last minute's cpm  to the multi minute FIFO
          loopsec = 0
          print("\n")
          
     
     if cfg.createHtml and enableHtml :
         printHtmlPage(cfg, d, (loopsec == 0))
         
     # LED indicator on high level
     if d.minute_cpsf.avr()*60 >= cfg.levelHigh :
         mio.highLed(True)
     else :
         mio.highLed(False)
         
     if not s4: # EXIT
        break
     
    
ser.close()
if cfg.isLogging :
    lf.close()
mio.logLed(False)
mio.highLed(False)
mio.serLed(False)

#outf.close()
