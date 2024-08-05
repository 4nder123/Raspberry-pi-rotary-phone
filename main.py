from handsfree import handsfree
from routing import audio_route
from threading import Thread
from dial import Dial
from gpiozero import Motor
import RPi.GPIO as GPIO
from time import sleep, time
from signal import pause
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import BluetoothController.bluezutils as bt

class rotaryphone:
    def __init__(self, hook, nr_tap, dial_switch):
        self.hook = hook
        self.nr_tap = nr_tap
        self.dial_switch = dial_switch
        GPIO.setup(hook, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(nr_tap, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(dial_switch , GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.motor = Motor(forward=17, backward=27)
        self.hf = handsfree()
        self.route = audio_route()    
        self.dial = Dial(self.nr_tap, self.dial_switch)
        self.is_call = False
        self.IsPhoneUp = GPIO.input(self.hook)
        
    
    def ring(self):
        while self.hf.get_calls_state() == "incoming" and GPIO.input(self.hook):
            t_end = time() + 2
            self.motor.forward()
            while time() < t_end and GPIO.input(self.hook):
                self.motor.reverse()
                sleep(0.025)
            else:
                t_end = time() + 3
                while GPIO.input(self.hook) and time() < t_end:
                    continue
        else:
            self.motor.stop()

    def get_number(self):
        self.dial.start()
        t_end = time() + 3
        while not GPIO.input(self.hook) and time() < t_end:
            if self.hf.get_calls_state() in ("active", "dialing"):
                break
            if self.dial.getnumber() == "" or self.dial.isCounting():
                t_end = time() + 3 
        else:
            self.dial.stop()
            if GPIO.input(self.hook):
                return ""
            else:
                return self.dial.getnumber()
        self.dial.stop()
        return ""
        
    def idle(self):
        while GPIO.input(self.hook):
            if bt.get_mac_address() != self.route.device_id:
                if bt.is_connected():
                    self.route.device_id = bt.get_mac_address()
                else:
                    bt.try_autoconnect()
                    sleep(10)
                    continue
            if self.is_call == True:
                self.route.clear_sound()
                self.hf.hangup()
                self.is_call = False
            if self.hf.get_calls_state() == "incoming":
                self.ring()
            else:
                sleep(1)
    
    def phone_up(self):
        if(self.hf.get_calls_state() == "incoming"):
            self.is_call = True
            self.hf.anwser_calls()
            self.route.on_call_start()
        elif (self.hf.get_calls_state() == "active" or self.hf.get_calls_state() == "dialing"):
            self.is_call = True
            self.route.on_call_start()
        else:
            nr = self.get_number()
            if nr == "0000":
                bt.unpair_all()
            if nr == "1111":
                bt.discovarable(True)
            elif nr == "":
                if self.hf.get_calls_state() in ("active", "dialing"):
                    self.is_call = True
                    self.route.on_call_start()
            else:
                self.hf.dial_number(nr)
                self.is_call = True
                self.route.on_call_start()

    def hook_event(self, channel):
        if not GPIO.input(self.hook) and not self.IsPhoneUp:
            self.IsPhoneUp = True
            self.phone_up()
        elif GPIO.input(self.hook) and self.IsPhoneUp:
            self.IsPhoneUp = False
            self.idle()
            

    def start(self):
        GPIO.add_event_detect(self.hook, GPIO.BOTH, callback=self.hook_event)
        GPIO.add_event_detect(self.nr_tap, GPIO.BOTH, callback=self.dial.addpulse)
        GPIO.add_event_detect(self.dial_switch, GPIO.BOTH, callback=self.dial.counter_change_status)
        self.hook_event(0)
       
    
if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    DBusGMainLoop(set_as_default=True)
    rp = rotaryphone(2, 3, 4)
    rp.start()
    GLib.MainLoop().run()
    

