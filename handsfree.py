import sys
import dbus

class handsfree:
    
    def __init__(self):
        self.bus = dbus.SystemBus()
        manager = dbus.Interface(self.bus.get_object('org.ofono', '/'),'org.ofono.Manager')
        self.modems = manager.GetModems()
        
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
        manager = dbus.Interface(self.bus.get_object('org.ofono', modem),
                                'org.ofono.VoiceCallManager')

        manager.HangupAll()
        
    def dial_number(self, number):
        pass

    def list_calls(self):
        pass
