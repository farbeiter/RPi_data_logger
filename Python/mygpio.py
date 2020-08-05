import RPi.GPIO as GPIO

PIN_LED_GREEN = 22
PIN_LED_RED = 18
PIN_LED_YELLOW = 36
PIN_LED_AMBER = 37


PIN_SWITCH_1 = 11
PIN_SWITCH_2 = 13
PIN_SWITCH_3 = 15
PIN_SWITCH_4 = 16

class myGPIO :
     def __init__(self, inLOG=PIN_SWITCH_1, outLOG=PIN_LED_GREEN, inAVR=PIN_SWITCH_2, outSER=PIN_LED_RED, outHIGH=PIN_LED_YELLOW) :
          self.pinInLOG = inLOG # switch to start/stop logging
          self.pinOutLOG = outLOG # indicator LED if logging is active
          self.pinInAVR = inAVR # switch to start/stop averaging
          self.pinOutSER = outSER # indicator LED during serial read from GM-counter
          self.pinOutHIGH = outHIGH
          GPIO.setmode(GPIO.BOARD) # refer to connector pin numbers 
          GPIO.setup(PIN_SWITCH_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
          GPIO.setup(PIN_SWITCH_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
          GPIO.setup(PIN_SWITCH_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
          GPIO.setup(PIN_SWITCH_4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
          GPIO.setup(self.pinOutLOG, GPIO.OUT)
          GPIO.setup(self.pinOutSER, GPIO.OUT)
          GPIO.setup(self.pinOutHIGH, GPIO.OUT)
          GPIO.output(self.pinOutLOG, False)
          GPIO.output(self.pinOutSER, False)
          GPIO.output(self.pinOutHIGH, False)

     def readSwitches(self) :
          a = GPIO.input(PIN_SWITCH_1)
          b = GPIO.input(PIN_SWITCH_2)
          c = GPIO.input(PIN_SWITCH_3)
          d = GPIO.input(PIN_SWITCH_4)
          return [a, b, c, d]
          
     def logLed(self, state) :
          if state :
               GPIO.output(self.pinOutLOG, True)
          else :
               GPIO.output(self.pinOutLOG, False)
          
     def serLed(self, state) :
          if state :
               GPIO.output(self.pinOutSER, True)
          else :
               GPIO.output(self.pinOutSER, False)
     
     def highLed(self, state):
          if state :
               GPIO.output(self.pinOutHIGH, True)
          else :
               GPIO.output(self.pinOutHIGH, False)
