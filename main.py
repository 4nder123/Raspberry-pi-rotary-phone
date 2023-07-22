from handsfree import handsfree
from routing import audio_route
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib



if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)
    hf = handsfree()
    route = audio_route()
    route.run()
    while True:
        ac = input("Action:" )
        if ac == "1":
            hf.anwser_calls()
        elif ac == "2":
            hf.hangup()
        elif ac == "3":
            ac = int(input("nr:" ))
            hf.dial(ac)
    GLib.MainLoop().run()
    

