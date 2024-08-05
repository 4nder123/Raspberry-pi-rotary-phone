import sys
import dbus

class handsfree:
    def anwser_calls(self):
        try:
            bus = dbus.SystemBus()
            manager = dbus.Interface(bus.get_object('org.ofono', '/'),'org.ofono.Manager')
            modems = manager.GetModems()
            for path, properties in modems:
                print("[ %s ]" % (path))
                if "org.ofono.VoiceCallManager" not in properties["Interfaces"]:
                    continue
                mgr = dbus.Interface(bus.get_object('org.ofono', path),'org.ofono.VoiceCallManager')
                calls = mgr.GetCalls()

                for path, properties in calls:
                    state = properties["State"]
                    print("[ %s ] %s" % (path, state))
                    if state != "incoming":
                        continue
                    call = dbus.Interface(bus.get_object('org.ofono', path),
                                    'org.ofono.VoiceCall')
                    
                    call.Answer()
        except:
            pass
            
    def hangup(self):
        try:
            bus = dbus.SystemBus()
            manager = dbus.Interface(bus.get_object('org.ofono', '/'),'org.ofono.Manager')
            modems = manager.GetModems()
            for path, properties in modems:
                print("[ %s ]" % (path))
                if "org.ofono.VoiceCallManager" not in properties["Interfaces"]:
                    continue
                mgr = dbus.Interface(bus.get_object('org.ofono', path),'org.ofono.VoiceCallManager')
                mgr.HangupAll()
                break
        except:
            pass
        
    def dial_number(self, number):
        try:
            bus = dbus.SystemBus()
            manager = dbus.Interface(bus.get_object('org.ofono', '/'),'org.ofono.Manager')
            modems = manager.GetModems()
            for path, properties in modems:
                print("[ %s ]" % (path))
                if "org.ofono.VoiceCallManager" not in properties["Interfaces"]:
                    continue
                mgr = dbus.Interface(bus.get_object('org.ofono', path),'org.ofono.VoiceCallManager')
                mgr.Dial(number, "default")
                break
        except:
            pass
            
    def get_calls_state(self):
        try:
            bus = dbus.SystemBus()
            manager = dbus.Interface(bus.get_object('org.ofono', '/'),'org.ofono.Manager')
            modems = manager.GetModems()  # Update list in case of new modems from newly-paired devices
            for modem, modem_props in modems:
                if "org.ofono.VoiceCallManager" not in modem_props["Interfaces"]:
                    continue
                mgr = dbus.Interface(bus.get_object('org.ofono', modem), 'org.ofono.VoiceCallManager')
                calls = mgr.GetCalls()
                    # Due to polling we aren't able to catch when calls end up disconnecting, so we just overwrite the list
                    # each time.
                for path, properties in calls:
                    return properties["State"]
        except:
            return ""
                