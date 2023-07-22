from handsfree import handsfree
from routing import audio_route
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)
    hf = handsfree()
    route = audio_route()
    if input("Action: ") == "1":
        hf.anwser_calls()
        route.on_call_start()
    GLib.MainLoop().run()
    

