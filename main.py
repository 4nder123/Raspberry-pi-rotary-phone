from handsfree import handsfree
from routing import audio_route
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

def poll():
        route = audio_route()
        while True:
            modems = manager.GetModems()  # Update list in case of new modems from newly-paired devices
            for modem, modem_props in modems:
                if "org.ofono.VoiceCallManager" not in modem_props["Interfaces"]:
                    continue
                mgr = dbus.Interface(bus.get_object('org.ofono', modem), 'org.ofono.VoiceCallManager')
                calls = mgr.GetCalls()
                # Due to polling we aren't able to catch when calls end up disconnecting, so we just overwrite the list
                # each time.
                currentcalls = {}
                for path, properties in calls:
                    state = properties['State']
                    name = properties['Name']
                    line_ident = properties['LineIdentification']

                    if state != "disconnected":
                        currentcalls[line_ident] = {
                            "path": path,
                            "state": state,
                            "name": name,
                            "modem": modem
                        }

                calls = currentcalls
                if len(calls) > 0:
                    route.on_call_start()
            sleep(1)

if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)
    hf = handsfree()
    thread = Thread(target=poll, daemon=True)
    thread.start()
    while True:
        ac = input("Action:" )
        if ac == "1":
            hf.anwser_calls()
        elif ac == "2":
            hf.hangup()
    GLib.MainLoop().run()
    

