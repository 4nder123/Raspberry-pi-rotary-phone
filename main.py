from handsfree import handsfree
from routing import audio_route
from gpiozero import Button
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import dbus

def get_number(nr_tap, dial_switch, hook):
    i = 0
    nr = 0
    nrid = ""
    pressed = True
    while hook.is_pressed:
        if i == 5000:
            break
        if dial_switch.is_pressed:
            i = 0
            if not nr_tap.is_pressed and pressed:
                pressed = False
                nr+=1
            elif nr_tap.is_pressed and not pressed:
                pressed = True  
        else:
            if nr == 10:
                nr = 0
            nrid = nrid + str(nr)
            nr = 0
        i += 1
        print(nrid)

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
        else:
            get_number(nr_tap, dial_switch, hook)
        if not hook.is_pressed and call_start:
            hf.hangup()
    GLib.MainLoop().run()
    

