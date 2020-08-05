import serial
import RPi.GPIO as GPIO
import time

ser = serial.Serial(
               port="/dev/serial0",
               baudrate = 9600,
               parity=serial.PARITY_NONE,
               stopbits=serial.STOPBITS_ONE,
               bytesize=serial.EIGHTBITS,
               timeout=30
           )
PIN_LED = 18
           
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN_LED, GPIO.OUT)

logcyc = 0 # cycling counter to time the log write events
print("# Please connect the MightyOhm Geiger Counter to serial UART and switch on.")
print("# (MightyOhm jumper J2 pin 5 (TX) ")
print("#  should be connected to pin 10 (RX) of the RPi 40-pin header)")
print("# If connected, the LED connected to RPI pin ", PIN_LED, " should flash once per second")
print("# Raw output from the Geiger Counter and evaluated values are displayed")
print("# (Typical CPM values for ambient conditions are in the range of 7 to 38)")
print("# Terminate by pressing Ctrl-C on the keyboard")
while 1 :
     # read serial output from migthyohm geiger counter
     GPIO.output(PIN_LED, True)
     #serial_line = "CPS, 1, CPM, 60, bla, bla, bla" # use for testing without geiger counter
     serial_line = ser.readline()
     #time.sleep(1) # use for testing without geiger counter
     GPIO.output(PIN_LED, False)
     time.sleep(0.05) # just to see the LED blink
     # analyse the serial output string
     items = str(serial_line).split(",")
     if len(items) != 7 :
          continue
     DEVCPS = int(items[1].strip())
     DEVCPM = int(items[3].strip())
     print("\nREAD FROM SERIAL : ", serial_line)
     print("EVALUATED        : ", end='')
     print("Cycle=",logcyc, "Device CPS=", DEVCPS, "Device CPM=", DEVCPM)
     logcyc += 1
