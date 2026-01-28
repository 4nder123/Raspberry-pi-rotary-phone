import dbus
from gi.repository import GLib

class HandsFree:
    def __init__(self):
        self.call_state = ""
        self.mgr = None
        self.bus = None

    def bt_connected(self):
        self._try_setup_modem()

    def _try_setup_modem(self, retries=10):
        try:
            self._setup_modem()
            self._connect_signals()
            print("HandsFree modem setup complete")
        except RuntimeError as e:
            if retries > 0:
                print(f"VoiceCallManager not ready, retrying... ({retries} left)")
                GLib.timeout_add(500, lambda: self._try_setup_modem(retries - 1) or False)
            else:
                print("Failed to setup modem:", e)

    def _get_modems(self):
        if self.bus is None:
            self.bus = dbus.SystemBus()
        manager = dbus.Interface(self.bus.get_object("org.ofono", "/"), "org.ofono.Manager")
        return self.bus, manager.GetModems()

    def _setup_modem(self):
        bus, modems = self._get_modems()

        for path, props in modems:
            if "org.ofono.VoiceCallManager" in props["Interfaces"]:
                self.mgr = dbus.Interface(
                    bus.get_object("org.ofono", path),
                    "org.ofono.VoiceCallManager"
                )
                return

        raise RuntimeError("No VoiceCallManager found")
    
    def _connect_signals(self):
        self.mgr.connect_to_signal("CallAdded", self._on_call_added)
        self.mgr.connect_to_signal("CallRemoved", self._on_call_removed)

    def _on_call_added(self, call_path, properties):
        state = properties.get("State", "")
        self.call_state = state
        print("CallAdded:", state)

        bus, modems = self._get_modems()
        call = dbus.Interface(bus.get_object("org.ofono", call_path), "org.ofono.VoiceCall")
        call.connect_to_signal("PropertyChanged", self._on_call_changed)

    def _on_call_removed(self, call_path):
        self.call_state = ""
        print("CallRemoved")

    def _on_call_changed(self, name, value):
        if name == "State":
            self.call_state = value
            print("CallChanged:", value)

    def answer_calls(self):
        try:
            bus, modems = self._get_modems()
            for path, props in modems:
                if "org.ofono.VoiceCallManager" not in props["Interfaces"]:
                    continue
                mgr = dbus.Interface(bus.get_object("org.ofono", path), "org.ofono.VoiceCallManager")
                for call_path, call_props in mgr.GetCalls():
                    if call_props["State"] != "incoming":
                        continue
                    call = dbus.Interface(bus.get_object("org.ofono", call_path), "org.ofono.VoiceCall")
                    call.Answer()
        except Exception as e:
            print("answer_calls error:", e)

    def hangup(self):
        try:
            bus, modems = self._get_modems()
            for path, props in modems:
                if "org.ofono.VoiceCallManager" not in props["Interfaces"]:
                    continue
                mgr = dbus.Interface(bus.get_object("org.ofono", path), "org.ofono.VoiceCallManager")
                mgr.HangupAll()
                break
        except Exception as e:
            print("hangup error:", e)

    def dial_number(self, number):
        try:
            bus, modems = self._get_modems()
            for path, props in modems:
                if "org.ofono.VoiceCallManager" not in props["Interfaces"]:
                    continue
                mgr = dbus.Interface(bus.get_object("org.ofono", path), "org.ofono.VoiceCallManager")
                mgr.Dial(number, "default")
                break
        except Exception as e:
            print("dial_number error:", e)

    def get_calls_state(self):
        return self.call_state