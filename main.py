from handsfree import handsfree
from subprocess import Popen, PIPE
from routing import audio_route
from threading import Thread
from gpiozero import Button
from time import sleep
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import dbus

def dial_sound(stop_sound):
    dial = Popen(["/usr/bin/aplay","-D","plughw:1,0","tone.wav"], stdout=PIPE, shell=False)
    while True:
        if stop_sound:
            dial.kill()

def get_number(nr_tap, dial_switch, hook):
    i = 0
    nr = 0
    nrid = ""
    pressed = True
    add = False
    stop_sound = False
    t = Thread(target=dial_sound, args = (lambda : stop_sound, ), daemon=True)
    t.start()
    while hook.is_pressed:
        if i == 300:
            stop_sound = True
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
        stop_sound = True
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
    call_start = False
    while True:
        if hook.is_pressed and hf.is_calls() and not call_start:
            hf.anwser_calls()
            call_start = True
        elif hook.is_pressed and not call_start and not hf.is_calls():
            call_start = True
            nr = get_number(nr_tap, dial_switch, hook)
            if nr != "":
                hf.dial_number(nr)
            else:
                call_start = False
        if not hook.is_pressed and call_start:
            call_start = False
            hf.hangup()
    GLib.MainLoop().run()
    

