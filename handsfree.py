import sys
import dbus

class handsfree:
    
    def __init__(self):
        self.bus = dbus.SystemBus()
        self.manager = dbus.Interface(self.bus.get_object('org.ofono', '/'),'org.ofono.Manager')
        self.modems = self.manager.GetModems()
        
    def anwser_calls(self):
        for path, properties in self.modems:
            print("[ %s ]" % (path))
            if "org.ofono.VoiceCallManager" not in properties["Interfaces"]:
                continue
            mgr = dbus.Interface(self.bus.get_object('org.ofono', path),
                            'org.ofono.VoiceCallManager')
            calls = mgr.GetCalls()

            for path, properties in calls:
                state = properties["State"]
                print("[ %s ] %s" % (path, state))
                if state != "incoming":
                    continue
                call = dbus.Interface(self.bus.get_object('org.ofono', path),
                                'org.ofono.VoiceCall')
                call.Answer()
            
    def hangup(self):
        modem = self.modems[0][0]
        mgr = dbus.Interface(self.bus.get_object('org.ofono', modem),
                                'org.ofono.VoiceCallManager')

        mgr.HangupAll()
        
    def dial_number(self, number):
        vcm = dbus.Interface(self.bus.get_object("org.ofono", self.modems[0][0]), "org.ofono.VoiceCallManager")
        vcm.Dial(number, "default")
        
    def is_calls(self):
        modems = self.manager.GetModems()  # Update list in case of new modems from newly-paired devices
        for modem, modem_props in modems:
            if "org.ofono.VoiceCallManager" not in modem_props["Interfaces"]:
                continue
            mgr = dbus.Interface(self.bus.get_object('org.ofono', modem), 'org.ofono.VoiceCallManager')
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
                return True
            elif len(calls) == 0:
                return False
