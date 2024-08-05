import RPi.GPIO as GPIO
from tone import Tone

class Dial:
    def __init__(self, nr_tap, dial_switch):
        self.pulse = 0
        self.numbers = ""
        self.tone = Tone(425, 11025)
        self.nr_tap = nr_tap
        self.dial_switch = dial_switch
        self.counter = False
        self.dialing = False
        self.addingpulse = False

    def start(self):
        self.dialing = True
        self.pulse = 0
        self.numbers = ""
        self.tone.play()

    def stop(self):
        self.dialing = False
        self.tone.stop()
        
    def counter_change_status(self, channel):
        if GPIO.input(self.dial_switch):
            if self.pulse > 0 and self.dialing:
                if self.pulse == 10:
                    self.numbers += "0"
                else:
                    self.numbers += str(self.pulse)    
            self.pulse = 0
            self.counter = False
        else:
            self.counter = True

    def addpulse(self, channel):
        if GPIO.input(self.nr_tap) and not self.addingpulse:
            self.addingpulse = True
            self.tone.pause()
            self.pulse += 1
        elif not GPIO.input(self.nr_tap) and self.addingpulse:
            self.tone.unpause()
            self.addingpulse = False

    def getnumber(self):
        return self.numbers
    
    def isCounting(self):
        return self.counter