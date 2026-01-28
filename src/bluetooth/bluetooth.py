import dbus 
import threading 
from time import sleep 
from dbus.mainloop.glib import DBusGMainLoop
import src.bluetooth.bt_helper as bt

class Bluetooth:
    def __init__(self, on_connected, on_disconnected, reconnect_interval=10):
        self.reconnect_interval = reconnect_interval
        self._reconnect_thread = None
        self._reconnect_running = False
        self.on_connected = on_connected
        self.on_disconnected = on_disconnected

        self._setup_dbus_listener()
        if not bt.is_connected(): 
            self._start_reconnect_thread()
        else:
            self._on_connected(None)

    def _setup_dbus_listener(self):
        bus = dbus.SystemBus()
        bus.add_signal_receiver(
            handler_function=self._properties_changed,
            dbus_interface="org.freedesktop.DBus.Properties",
            signal_name="PropertiesChanged",
            arg0="org.bluez.Device1",
            path_keyword="path"
        )

    def _properties_changed(self, iface, changed, invalidated, path=None):
        print("Bluetooth properties changed:", iface, changed, path)
        if "Connected" in changed:
            connected = bool(changed["Connected"])
            if connected:
                self._on_connected(path)
            else:
                self._on_disconnected(path)
            return
        if "Paired" in changed and bool(changed["Paired"]):
            print("New device paired, checking connection...")
            if bt.is_connected():
                self._on_connected(path)
            return
        
    def _on_connected(self, path):
        mac = bt.get_mac_address()
        bt.save_mac(mac)
        self._reconnect_running = False
        self.on_connected(mac)

    def _on_disconnected(self, path):
        self._start_reconnect_thread()
        self.on_disconnected()

    def clear_paired_devices(self):
        bt.clear_paired_devices()
    
    def set_discoverable(self, discoverable):
        bt.set_discoverable(discoverable)

    def _start_reconnect_thread(self):
        if self._reconnect_running:
            return

        self._reconnect_running = True

        self._reconnect_thread = threading.Thread(
            target=self._reconnect_worker,
            daemon=True
        )
        self._reconnect_thread.start()

    def _reconnect_worker(self):
        mac = bt.load_last_mac()
        if not mac:
            print("No last known MAC address, cannot reconnect")
            self._reconnect_running = False
            return
        while self._reconnect_running and not bt.is_connected():
            if bt.connect_mac(mac):
                continue
            sleep(self.reconnect_interval)
        print("Bluetooth reconnect thread exiting")
        self._reconnect_running = False

