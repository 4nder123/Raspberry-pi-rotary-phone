from handsfree import handsfree
from subprocess import Popen, PIPE
from routing import audio_route
from threading import Thread
from gpiozero import Button, Motor
from time import sleep
import time
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import dbus

def ring(motor, hf):
    while True:
        while hf.get_calls_state() == "incoming":
            t_end = time.time() + 2
            while time.time() < t_end:
                motor.forward()
                sleep(0.025)
                motor.backward()
                sleep(0.025)
            sleep(3)
        else:
            motor.stop()

def get_number(nr_tap, dial_switch, hook, route):
    i = 0
    nr = 0
    nrid = ""
    pressed = True
    add = False
    stop_sound = False
    sleep(1)
    t = Thread(target=route.dial_sound, daemon=True)
    t.start()
    while hook.is_pressed:
        if i == 300 and nrid != "":
            route.close_dial_sound()
            t.join()
            return nrid
        if dial_switch.is_pressed:
            i = 0
            add = True
            if not nr_tap.is_pressed and pressed:
                pressed = False
                nr+=1
            elif nr_tap.is_pressed and not pressed:
                pressed = True  
        elif add:
            add = False
            if nr == 10:
                nr = 0
            nrid = nrid + str(nr)
            nr = 0
        i += 1
        sleep(0.01)
    else:
        nrid = ""
        route.close_dial_sound()
        t.join()
        return nrid

if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)
    hf = handsfree()
    route = audio_route()
    route.run()
    bus = dbus.SystemBus()
    manager = dbus.Interface(bus.get_object('org.ofono', '/'), 'org.ofono.Manager')
    hook = Button(2)
    nr_tap = Button(3)
    dial_switch = Button(4)
    motor = Motor(forward=17, backward=27)
    t = Thread(target=ring, args=(motor, hf), daemon=True)
    t.start()
    call_start = False
    while True:
        if hook.is_pressed and hf.is_calls() and not call_start:
            hf.anwser_calls()
            call_start = True
        elif hook.is_pressed and not call_start and not hf.is_calls():
            call_start = True
            nr = get_number(nr_tap, dial_switch, hook, route)
            if nr != "":
                hf.dial_number(nr)
        if not hook.is_pressed and call_start:
            call_start = False
            hf.hangup()
    GLib.MainLoop().run()
    

