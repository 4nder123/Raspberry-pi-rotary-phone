from handsfree import handsfree
from routing import audio_route
from bluetooth import bluetooth
from threading import Thread
from gpiozero import Button, Motor
from time import sleep
import time
from subprocess import call
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

class rotaryphone:
    def __init__(self):
        self.hook = Button(2)
        self.nr_tap = Button(3)
        self.dial_switch = Button(4)
        self.motor = Motor(forward=17, backward=27)
        self.hf = handsfree()
        self.route = audio_route()
        self.ringer = Thread(target=self.ring, daemon=True)
        self.dial_sound = Thread(target=route.dial_sound, daemon=True)
        self.bluealsa = "/usr/bin/bluealsa"
        self.call_start = False
        self.dial_pressed = False
    
    def start_ofono:
        call(["sudo", self.bluealsa, "-p", "hfp-ofono"])
    
    def ring(self):
        while True:
            while self.hf.get_calls_state() == "incoming":
                t_end = time.time() + 2
                while time.time() < t_end:
                    self.motor.forward()
                    sleep(0.025)
                    self.motor.backward()
                    sleep(0.025)
                sleep(3)
            else:
                self.motor.stop()
            sleep(1)

    def get_number(self):
        nr = 0
        nrid = ""
        sleep(1)
        t_end = time.time() + 3
        self.dial_sound.start()
        while self.hook.is_pressed or time.time() < t_end:
            if self.dial_switch.is_pressed:
                t_end = time.time() + 3
                if not self.nr_tap.is_pressed and self.dial_pressed:
                    self.dial_pressed = False
                    nr+=1
                elif self.nr_tap.is_pressed and not self.dial_pressed:
                    self.dial_pressed = True  
            elif nr != 0:
                if nr == 10:
                    nr = 0
                nrid = nrid + str(nr)
                nr = 0
        else:
            if not self.hook.is_pressed:
                nrid = ""
            self.route.close_dial_sound()
            self.dial_sound.join()
            return nrid
        
    def run(self):
        self.start_ofono
        self.route.run()
        self.ringer.start()
        while True:
            if self.hook.is_pressed and self.hf.is_calls() and not self.call_start:
                self.hf.anwser_calls()
                self.call_start = True
            elif self.hook.is_pressed and not self.call_start and not self.hf.is_calls():
                self.call_start = True
                nr = self.get_number()
                if nr != "":
                    self.hf.dial_number(nr)
            if not self.hook.is_pressed and self.call_start:
                self.call_start = False
                self.hf.hangup()
    
if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)
    rp = rotaryphone()
    rp.run()
    GLib.MainLoop().run()
    

