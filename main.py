from handsfree import handsfree
from routing import audio_route
from gpiozero import Button
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import dbus

def get_number(nr_tap, dial_switch, hook):
    i = 0
    while hook.is_pressed:
        if dial_switch.is_pressed:
            if not nr_tap.is_pressed:
                i+=1
        else:
            print(i)

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
    call_start = None
    while True:
        if hook.is_pressed and hf.is_calls(bus, manager):
            hf.anwser_calls()
            call_start = True
        else:
            pass
       if not hook.is_pressed and call_start = False:
           hf.hangup()
    GLib.MainLoop().run()
    

