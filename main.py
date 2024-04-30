from handsfree import handsfree
from routing import audio_route
from bluetooth import bluetooth
from gpiozero import Button, Motor
from time import sleep, time
from signal import pause
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

class rotaryphone:
    def __init__(self):
        self.hook = Button(2)
        self.nr_tap = Button(3)
        self.dial_switch = Button(4)
        self.motor = Motor(forward=17, backward=27)
        self.hf = handsfree()
        self.bt = bluetooth()
        self.route = audio_route()    
        self.is_call = False
    
    def ring(self):
        while self.hf.get_calls_state() == "incoming" and not self.hook.is_pressed:
            t_end = time() + 2
            self.motor.forward()
            while time() < t_end:
                self.motor.reverse()
                sleep(0.025)
            sleep(3)
        else:
            self.motor.stop()

    def get_number(self):
        nr = 0
        nrid = ""
        t_end = time() + 3
        dial_pressed = False
        call_state = self.hf.get_calls_state()
        self.route.dial_sound()
        while self.hook.is_pressed and time() < t_end:
            if not dial_pressed and (call_state == "active" or call_state == "dialing"):
                nrid = ""
                break
            if nrid == "":
                t_end = time() + 3
            if self.dial_switch.is_pressed:
                t_end = time() + 3
                if not self.nr_tap.is_pressed and dial_pressed:
                    dial_pressed = False
                    nr+=1
                elif self.nr_tap.is_pressed and not dial_pressed:
                    dial_pressed = True 
            elif nr != 0:
                if nr == 10:
                    nr = 0
                nrid += str(nr)
                nr = 0
            call_state = self.hf.get_calls_state()    
        else:
            if not self.hook.is_pressed:
                nrid = ""
        self.route.close_dial_sound()
        return nrid
        
    def idle(self):
        while not self.hook.is_pressed:
            if self.bt.get_mac_address() != self.route.device_id:
                if self.bt.is_connected:
                    self.bt.discovarable(False)
                    self.route.device_id = self.bt.get_mac_address()
                else:
                    self.bt.discovarable(True)
                    self.bt.try_autoconnect()
                    continue
            if self.is_call == True:
                self.route.clear_sound()
                self.hf.hangup()
                self.is_call = False
            if self.hf.get_calls_state() == "incoming":
                self.ring()
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
                self.bt.unpair_all()
            elif nr == "":
                self.is_call = True
                self.route.on_call_start()
            else:
                self.hf.dial_number(nr)
                self.is_call = True
                self.route.on_call_start()
            

    def run(self):
        self.hook.when_released = self.idle
        self.hook.when_pressed = self.phone_up 
        self.idle()
        pause()
       
    
if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)
    rp = rotaryphone()
    rp.run()
    GLib.MainLoop().run()
    

