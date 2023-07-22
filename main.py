from handsfree import handsfree
from routing import audio_route
from gi.repository import GLib

if __name__ == '__main__':
    hf = handsfree()
    route = audio_route()
    if input("Action: ") == "1":
        hf.anwser_calls()
        route.on_call_start()
    
    GLib.MainLoop().run()
    

